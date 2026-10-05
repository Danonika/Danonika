"""Check aggregation boundaries without credentials or private data."""
import unittest
import xml.etree.ElementTree as ET

from code_changes import HISTORY, REPOSITORIES, collect, next_cursor, render


def connection(nodes, cursor=None):
    return {'nodes': nodes, 'pageInfo': {'hasNextPage': cursor is not None,
                                      'endCursor': cursor}}


def commit(oid, additions, deletions, parents=1):
    return {'oid': oid, 'additions': additions, 'deletions': deletions,
            'parents': {'totalCount': parents}}


class AggregationTests(unittest.TestCase):
    def test_pagination_merge_exclusion_and_deduplication(self):
        def query(document, variables):
            cursor = variables['cursor']
            if document == REPOSITORIES:
                self.assertEqual(variables['login'], 'example')
                head = 'head-1' if cursor is None else 'head-2'
                repos = [{'defaultBranchRef': {'target': {'id': head}}}]
                if cursor is None:
                    repos.append({'defaultBranchRef': None})  # Empty repository.
                return {'user': {'id': 'author-id', 'repositories':
                        connection(repos, 'repos-2' if cursor is None else None)}}
            self.assertEqual(document, HISTORY)
            self.assertEqual(variables['author'], 'author-id')
            self.assertEqual((variables['since'], variables['until']), ('start', 'end'))
            if variables['id'] == 'head-2':
                nodes = [commit('a', 10, 2), commit('c', 7, 4)]
                page = None
            elif cursor is None:
                nodes = [commit('a', 10, 2), commit('merge', 900, 800, parents=2)]
                page = 'commits-2'
            else:
                nodes = [commit('b', 20, 3, parents=0)]
                page = None
            return {'node': {'history': connection(nodes, page)}}

        self.assertEqual(collect('example', 'start', 'end', query),
                         {'additions': 37, 'deletions': 9, 'commits': 3,
                          'since': 'start', 'until': 'end'})

    def test_no_partial_result_when_later_history_fails(self):
        def query(document, variables):
            if document == REPOSITORIES:
                return {'user': {'id': 'author', 'repositories': connection([
                    {'defaultBranchRef': {'target': {'id': 'head'}}}])}}
            if variables['cursor'] is None:
                return {'node': {'history': connection([commit('a', 50, 10)], 'next')}}
            return {'node': None}
        with self.assertRaisesRegex(RuntimeError, 'no partial totals'):
            collect('example', 'start', 'end', query)

    def test_repeated_cursor_fails(self):
        with self.assertRaisesRegex(RuntimeError, 'pagination'):
            next_cursor(connection([], 'same'), 'same')

    def test_empty_history_reports_zero(self):
        def query(document, variables):
            return {'user': {'id': 'author', 'repositories': connection([])}}
        result = collect('example', 'start', 'end', query)
        self.assertEqual((result['additions'], result['deletions'], result['commits']),
                         (0, 0, 0))

    def test_svg_has_exact_aggregate_values_and_period(self):
        stats = {'additions': 1234567, 'deletions': 89012,
                 'since': '2025-10-05T00:00:00Z', 'until': '2026-10-05T00:00:00Z'}
        for dark in (False, True):
            svg = render(stats, dark)
            root = ET.fromstring(svg)
            self.assertEqual(root.attrib['viewBox'], '0 0 480 100')
            self.assertIn('+1,234,567', svg)
            self.assertIn('−89,012', svg)
            self.assertIn('2025-10-05 — 2026-10-05', svg)


if __name__ == '__main__':
    unittest.main()
