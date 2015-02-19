$(document).ready(function() {

function renderChart(jsonData, yField, xField, legend) {
    $('#graph').empty();
    $('#chartsModal').modal('show');
    $('.modal-body').scrollTop(0)
    var margin = {top: 0, right: 100, bottom: 100, left: 175},
    width = 520 - margin.left - margin.right,
    height = 300 - margin.top - margin.bottom;

    var parseDate = d3.time.format("%Y-%m-%m-%H-%M").parse;

    var x = d3.time.scale()
    .range([0, width]);

    var y = d3.scale.linear()
    .range([height, 0]);

    var xAxis = d3.svg.axis()
    .scale(x)
    .ticks(d3.time.minutes, 15)
    .orient("bottom");

    var yAxis = d3.svg.axis()
    .scale(y)
    .ticks(4)
    .orient("left");

    var line = d3.svg.line()
    .x(function(d) { return x(d.date); })
    .y(function(d) { return y(d.value); });

    var svg = d3.select("#graph").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    data = jsonData.rows;
    $('#chartHeading').text(legend);
    data.forEach(function(d) {
            d.date = new Date(d[yField]*1000);
            d.value = +d[xField];
            });

    x.domain(d3.extent(data, function(d) { return d.date; }));

    var e = d3.extent(data, function(d) { return d.value;});
    e = [e[0]-1,e[1]+1];

    y.domain(e);

    svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .attr("x", 5)
    .call(xAxis);

    svg.append("g")
    .attr("class", "y axis")
    .call(yAxis)
    .append("text")
    .attr("transform", "rotate(-90)")
    .attr("y", 6)
    .attr("dy", ".71em")
    .style("text-anchor", "end")
    .text(legend)
    .attr("class", "legend");

    svg.append("path")
    .datum(data)
    .attr("class", "line")
    .attr("d", line);
}

$('.nodesLabel, .nodesValue').click(function() {
        var jsonData = window.pageAnalyticsData;
        renderChart(jsonData, "MinuteTime", "count_hostname", "Node Count");
});
$('.cpuLabel, .cpuValue').click(function() {
        var jsonData = window.pageAnalyticsData;
        renderChart(jsonData, "MinuteTime", "avg_cpu", "Average Cpu");
});
$('.bandwidthLabel, .bandwidthValue').click(function() {
        var jsonData = window.pageBandData;
        renderChart(jsonData, "MinuteTime", "sum_computed_bytes_sent_div_elapsed", "Bandwidth");
});

})
