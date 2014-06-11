google.load('visualization', '1', {'packages' : ['controls','table','corechart','geochart']});

function renderChart(newStyle, dialog, container, dataSourceUrl, yColumn, xColumn, aggFunc, options) {
    if ( newStyle ) {
        $(dialog).dialog("open");
    }
    else {
        $(container).empty();
        $(dialog).modal('show');
        $('.modal-body').scrollTop(0);
    }

    startQuery(container, dataSourceUrl, yColumn, xColumn, aggFunc, options)
}

function startQuery(container, dataSourceUrl, yColumn, xColumn, aggFunc, options) {
    var query = new google.visualization.Query(dataSourceUrl);
    query && query.abort();
    query.send(function(response) {handleResponse_psg(container, dataSourceUrl, response, yColumn, xColumn, aggFunc, options);});
}

// NOTE: appended _psg to showLine() and handleResponse() to prevent conflict
//       with Sapan's analytics page.

function agg_bandwidth(arr) {
        var ret = 0;
        for (var i = 0; i < arr.length; i++) {
                ret+=arr[i]*8.0/1024.0/1024.0/1024.0;
        }
        return ret;
}

function showLine_psg(container, dt, options) {
    var base_options = {
            'width': 520,
            'height': 300,
  	    'pages': true,
	    'numRows': 9,
            'backgroundColor': 'transparent',
            'titleTextStyle': {"color": "black"},
            'legend': 'none',
            'hAxis': {"baselineColor": "darkBlue",
                      "textStyle": {"color": "black"}},
            'vAxis': {"baselineColor": "darkBlue",
                      "textStyle": {"color": "black"}},
          }

    options = $.extend(true, {}, base_options, options);

    var lineChart = new google.visualization.ChartWrapper({
          'chartType': 'LineChart',
          'containerId': container.substring(1),
          'view': {'columns': [0, 1]},
          'options': options
        });
        lineChart.setDataTable(dt);
        lineChart.draw();

}

function fixDate(unixDate) {
    return new Date(unixDate*1000);
}

function fixDate2(unixDate) {
    return new Date(unixDate);
}

function handleResponse_psg(container, dataSourceUrl, response, yColumn, xColumn, aggFunc, options) {
    var supportedClasses = {
                    'Table':google.visualization.Table,
                    'LineChart':google.visualization.LineChart,
                    'ScatterChart':google.visualization.ScatterChart,
                    'ColumnChart':google.visualization.ColumnChart,
                    'GeoChart':google.visualization.GeoChart,
                    'PieChart':google.visualization.PieChart,
                    'Histogram':google.visualization.Histogram};

    if (response.isError()) {
        //console.log("retry chart");
        setTimeout(function () { startQuery(container, dataSourceUrl, yColumn, xColumn, aggFunc, options) }, 5000);
        return
    }

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
           modifier: fixDate2,
           }],
           [{
            column: xColumn,
            type: 'number',
            label: dt.getColumnLabel(xColumn),
            aggregation: aggFunc}]);

        showLine_psg(container, groupedData1, options);
    });

    proxy.setDataTable(response.getDataTable());

    proxy.draw();
}


