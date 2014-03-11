$(document).ready(function() {

	
	function getServerData(url, label, value) {
		var jqxhr = $.getJSON( url, function(data) {
			if (value == 'nodesValue') {
				var unit = '';
				window.nodesCnt = data;
			} else if (value == 'cpuValue'){
				var unit = '%';
				window.cpuCnt = data;
			} else if (value == 'bandwidthValue'){
				var unit = '';
				window.bandData = data;
			}
			var legend = data.legend;
			var data = data.data;
			var dataLength = data.length - 1;
			$('.'+label).text(legend).show();
			$('.'+value).text(Math.round(data[dataLength][1])+unit).show();
		})
		
	}
	var selectedNodeTxt = $('.currentOriginalNode').text();
	selectedNodeTxt = selectedNodeTxt.trim();
	selectedNodeTxt = selectedNodeTxt.split(' ').join('');//selectedNodeTxt.replace(" ", "")
	var parentNodeTxt = $('.selectedMainNav').text();
	parentNodeTxt = parentNodeTxt.replace("/\n","");
 	parentNodeTxt = parentNodeTxt.replace("»","");
	parentNodeTxt = parentNodeTxt.trim();
	
	baseNodeQuery = 'SELECT Minute(time) as Minute,COUNT(distinct %hostname) FROM [vicci.demoevents]';
	baseCpuQuery = 'SELECT Minute(time) as Minute,AVG(i0) as Cpu FROM [vicci.demoevents]';
	baseBwQuery = 'SELECT Minute(time) as Minute,AVG(i1) as Requests FROM [vicci.demoevents]';
	groupByClause = ' GROUP BY Minute ORDER BY Minute';

	if (selectedNodeTxt ) {
		if (parentNodeTxt.length > 0 && parentNodeTxt.charAt(parentNodeTxt.length-1)=='s') {
			parentNodeTxt = parentNodeTxt.substring(0, parentNodeTxt.length-1);
		}
		if (parentNodeTxt=='Slice') {
			whereClause = " WHERE s3='"+selectedNodeTxt+"'";
		} 
		else if (parentNodeTxt=='Site') {
			whereClause = " WHERE s2='"+selectedNodeTxt+"' OR %hostname CONTAINS '"+selectedNodeTxt+"'";
		} 
		else if (parentNodeTxt=='Node') {
			whereClause = " WHERE %hostname='"+selectedNodeTxt+"'";
			alert(whereClause);
		} else {
			console.log('Error: Unkown object type:'+parentNodeTxt);
		}
	} else {
		whereClause = '';
	}
	finalNodeQuery = encodeURIComponent(baseNodeQuery + whereClause + groupByClause);
	finalCpuQuery = encodeURIComponent(baseCpuQuery + whereClause + groupByClause);
	finalBwQuery = encodeURIComponent(baseBwQuery + whereClause + groupByClause);
	getServerData('http://cloud-scrutiny.appspot.com/command?action=send_query&legend=Node+Count&tqx=saber&q='+finalNodeQuery,'nodesLabel','nodesValue');
	getServerData('http://cloud-scrutiny.appspot.com/command?action=send_query&legend=Load&tqx=saber&q='+finalCpuQuery,'cpuLabel','cpuValue');
	getServerData('http://cloud-scrutiny.appspot.com/command?action=send_query&legend=Bandwidth&tqx=saber&q='+finalBwQuery,'bandwidthLabel','bandwidthValue');

	$('.nodesLabel, .nodesValue').click(function() {
		var jsonData = window.nodesCnt;
		renderChart(jsonData);
	});
	$('.cpuLabel, .cpuValue').click(function() {
		var jsonData = window.cpuCnt;
		renderChart(jsonData);
	});
	$('.bandwidthLabel, .bandwidthValue').click(function() {
		var jsonData = window.bandData;
		renderChart(jsonData);
	});

	function renderChart(jsonData) {
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

		/*var data_path = "http://sabertooth.cs.princeton.edu/graphs/UpNodes";
		d3.json(data_path, function(error, input) {*/
			//jsonData = JSON.stringify(eval("(" + jsonData + ")"));
			data = jsonData.data;//input['data'];
			legend = jsonData.legend;//input['legend']
			$('#chartHeading').text(legend);
			data.forEach(function(d) {
				d.date = new Date(d[0]*1000);
				d.value = +d[1];
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
				//});
	}

})
