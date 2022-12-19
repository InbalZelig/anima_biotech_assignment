from conf import COLUMN_HEADER, ROW_HEADER, COMPOUND_HEADER


class Well:
    def __init__(self, row, column):
        self.row = row
        self.column = column

    def get_compound_name(self, assay_df) -> str:
        compound_df = assay_df[(assay_df[ROW_HEADER] == self.row) & (assay_df[COLUMN_HEADER] == self.column)]
        return compound_df[COMPOUND_HEADER].values[0]
