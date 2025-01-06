from typing import Any, Optional

from benchmarks.pybench.persistence.common import BenchAccessProto, BenchOperator, BenchRecord


class FileSystemBenchOperator(BenchOperator):

    def __init__(self, accessor: BenchAccessProto):
        self.accessor = accessor

    def write_bench_result(self, record: BenchRecord) -> None:
        result_file = self.accessor.bench_result_file(record["global_id"])
        result_file.write_text(record["data"])

    def get_all_bench_results(self):
        content_container = []
        for schema in self.accessor.schemas:
            path = self.accessor.bench_result_file(self.accessor.get_id(schema))
            content_container.append(
                path.read_text(),
            )
        return content_container

    def get_bench_result(self, schema: Any) -> Optional[str]:
        try:
            return self.accessor.bench_result_file(self.accessor.get_id(schema)).read_text()
        except FileNotFoundError:
            return None


def filesystem_operator_factory(accessor: BenchAccessProto) -> FileSystemBenchOperator:
    return FileSystemBenchOperator(accessor)
