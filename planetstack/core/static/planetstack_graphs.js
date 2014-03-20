google.load('visualization', '1', {'packages' : ['controls','table','corechart','geochart']});

function renderChart(origQuery, yColumn, xColumn, title) {
    $('#graph').empty();
    $('#chartsModal').modal('show');
    $('.modal-body').scrollTop(0)

    var queryString = encodeURIComponent(origQuery);
    var serverPart = "http://cloud-scrutiny.appspot.com/command?table=demoevents&action=send_query&force=ColumnChart&q=";
    var dataSourceUrl = serverPart + queryString;

    //var dataSourceUrl = "http://node36.princeton.vicci.org:8000/analytics/bigquery/?avg=%25cpu&count=%25hostname&format=raw";

    var query = new google.visualization.Query(dataSourceUrl)
    query && query.abort();
    console.log("query.send")
    query.send(function(response) {handleResponse_psg(response, yColumn, xColumn, title);});
    console.log("query.sent")
}

// NOTE: appended _psg to showLine() and handleResponse() to prevent conflict
//       with Sapan's analytics page.

function showLine_psg(dt, title) {
    console.log("showline")
    var lineChart = new google.visualization.ChartWrapper({
          'chartType': 'LineChart',
          'containerId': 'graph',
          'options': {
            'width': 520,
            'height': 300,
            'title': title,
  	    'pages': true,
	    'numRows': 9,
            'backgroundColor': 'transparent',
            'titleTextStyle': {"color": "white"},
            'legend': 'none',
//            'legend': {"textStyle": {"color": "white"}},
            'hAxis': {"baselineColor": "white",
                      "textStyle": {"color": "white"}},
            'vAxis': {"baselineColor": "white",
                      "textStyle": {"color": "white"}},
          },
          'view': {'columns': [0, 1]}
        });
        lineChart.setDataTable(dt);
        lineChart.draw();
}

function fixDate(unixDate) {
    return new Date(unixDate*1000);
}

function handleResponse_psg(response, yColumn, xColumn, title) {
    console.log("handleResponse")

    var supportedClasses = {
                    'Table':google.visualization.Table,
                    'LineChart':google.visualization.LineChart,
                    'ScatterChart':google.visualization.ScatterChart,
                    'ColumnChart':google.visualization.ColumnChart,
                    'GeoChart':google.visualization.GeoChart,
                    'PieChart':google.visualization.PieChart,
                    'Histogram':google.visualization.Histogram};

    var proxy = new google.visualization.ChartWrapper({
      'chartType': 'Table',
      'containerId': 'graph_work',
      'options': {
        'width': 800,
        'height': 300,
         pageSize:5,
         page:'enable',
        'legend': 'none',
        'title': 'Nodes'
      },
      'view': {'columns': [0,1]}
    });

    google.visualization.events.addListener(proxy, 'ready', function () {
        var dt = proxy.getDataTable();
        var groupedData1 = google.visualization.data.group(dt, [{
           column: yColumn,
           type: 'datetime',
           modifier: fixDate,
           }],
           [{
            column: xColumn,
            type: 'number',
            label: dt.getColumnLabel(xColumn),
            aggregation: google.visualization.data.sum}]);

        showLine_psg(groupedData1, title);

        console.log(xColumn);
    });

    console.log(response.getReasons());
    console.log(response.getDataTable());
    console.log(response.getDetailedMessage());
    console.log(response.getMessage());

    proxy.setDataTable(response.getDataTable());

    proxy.draw();
}

$('.nodesLabel, .nodesValue').click(function() {
        var jsonData = window.pageAnalyticsData;
        renderChart(jsonData.query, 0, 2, "Node Count");
        //renderChartJson(jsonData, "MinuteTime", "count_hostname", "Node Count");
});

$('.cpuLabel, .cpuValue').click(function() {
        var jsonData = window.pageAnalyticsData;
        renderChart(jsonData.query, 0, 1, "Average CPU");
});
$('.bandwidthLabel, .bandwidthValue').click(function() {
        var jsonData = window.pageBandData;
        renderChart(jsonData.query, 0, 1, "Total Bandwidth");
});
