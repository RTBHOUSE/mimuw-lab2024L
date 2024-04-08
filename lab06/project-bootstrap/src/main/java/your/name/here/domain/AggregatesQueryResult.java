package your.name.here.domain;

import java.util.List;

public class AggregatesQueryResult {

    private List<String> columns;
    private List<List<String>> rows;

    public AggregatesQueryResult() {
    }

    public AggregatesQueryResult(List<String> columns, List<List<String>> rows) {
        this.columns = columns;
        this.rows = rows;
    }

    public List<String> getColumns() {
        return columns;
    }

    public void setColumns(List<String> columns) {
        this.columns = columns;
    }

    public List<List<String>> getRows() {
        return rows;
    }

    public void setRows(List<List<String>> rows) {
        this.rows = rows;
    }
}