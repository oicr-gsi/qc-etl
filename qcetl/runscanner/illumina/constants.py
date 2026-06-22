from enum import Enum
from qcetl.column import RunScannerFlowcellColumn as FlowColumn


class LEVEL:
    FLOWCELL = "flow_cell"
    INDEX = "Index"
    LANE = "lane"
    READ = "Read"


class KEY:
    HEALTHTYPE = "healthType"
    STARTDATE = "startDate"
    COMPLETIONDATE = "completionDate"
    CLUSTERS = "Clusters"
    CLUSTERSPF = "Clusters PF"


class METRIC(Enum):
    CHART = "chart"
    TABLE = "table"
    YIELD_BY_READ = "illumina-yield-by-read"
    CLUSTERS_BY_LANE = "illumina-clusters-by-lane"


#: Keys that are numbers, but have comma, percent sign
KEY_NUMBERS = ["% > Q30", "Clusters", "Clusters PF", "Density %"]

#: The types of the columns in the flow cell table

FLOW_CELL_TYPES = {
    FlowColumn.CompletionDate: "datetime64[ns, UTC]",
    FlowColumn.StartDate: "datetime64[ns, UTC]",
    FlowColumn.IndexLengths: str,
}
