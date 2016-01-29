
$(document).ready(function(){
    chartHeight = 300-
                  $(".status-chart").find($(".title")).outerHeight();
    bisect = d3.bisector(function(datum) {
      return datum.key;
    }).right;

    });

function renderHist(hist){
    var height = chartHeight+50,
        width = height,
        radius = width/2;
    var bright=d3.rgb("#5595c7");
    var dark=d3.rgb("#24587A");
    color = d3.scale.linear().domain([0,1])
                .range([bright,dark]);
    colorLight = d3.scale.linear().domain([0,1])
                .range([bright.brighter(), dark.brighter()]);
    var outerRadius=radius-10
    var arc = d3.svg.arc()
              .outerRadius(outerRadius)
              .innerRadius(0);
    var pie = d3.layout.pie().value(function(d){return d.value})
              .sort(null)
    var svg = d3.select(".status-chart").append("svg")
                .attr("width",width)
                .attr("height",height)
    var arcs = svg.selectAll("g.arc").data(pie(d3.entries(hist)))
                .enter().append("g").attr("class","arc")
                .attr("transform", "translate(" +
                outerRadius + "," + outerRadius + ")");

    //Draw arc paths
    arcs.append("path").attr("d", arc)
            .attr('id', function(d){return d.data.key})
            .attr('fill', function(d,i){
                return color(d.value);})
            .on("mouseover", function(d,i) {
                d3.select(this).transition()
                .attr('fill', function(d,i){ return colorLight(d.value);})
                .duration('100')
            }).on("mouseout", function(d,i) {
                d3.select(this).transition()
                .attr('fill', function(d,i){return color(d.value);})
                .duration('100')});
    
    arcs.append("text").attr("transform", function(d){
            return "translate(" + arc.centroid(d) + ")";
            }).attr("text-anchor","middle")
            .text(function(d){return d.data.key})
            .style("display", function(d){if (d.value==0){return "none";} return "block"})
    
    // redirect to category page
    $(".status-chart").find("path").click(function(){
        location.href=("/categories?status=" + $(this).attr("id"));
    })

    };
    



function renderCatHist(catHist){
    var margin = {top: 20, right: 80, bottom:20, left: 80},
    width = $(".cat-status-chart").width() - margin.left - margin.right,
    height = chartHeight-30;

    var x = d3.scale.ordinal()
        .rangeRoundBands([0, width], .1);

    var y = d3.scale.linear()
        .range([height, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .ticks(10, "%");

    var svg = d3.select(".cat-status-chart").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    var data=d3.entries(catHist);
    x.domain(d3.keys(catHist));
    y.domain([0, 1]);

    svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

    svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Completion");

    svg.selectAll(".bar")
      .data(data)
    .enter().append("rect")
      .attr("class", "bar")
      .attr("x", function(d) { return x(d.key); })
      .attr("id",function(d) { return d.key;})
      .attr("width", x.rangeBand())
      .attr("y", function(d) { return y(d.value); })
      .attr("height", function(d) { return height - y(d.value); });

    // redirect to category page
    $(".bar").click(function(){
        location.href=("/categories?category=" + $(this).attr("id"));

    })
}

function renderActivity(activity){
  var margin = {top: 20, right: 100, bottom: 30, left: 100},
    width = $(".activity-chart").width() - margin.left - margin.right,
    height = chartHeight;
  newDate= null;
  activity=activity;
  if (Object.keys(activity).length == 1){
    for (key in activity){newDate=new Date(Date.parse(key))}
    newDate = new Date(newDate.setDate(newDate.getDate()-1));
    activity[newDate.toJSON().split("T")[0]]=0
  }
  
  parseDate = d3.time.format("%Y-%m-%d").parse;
  
  var x = d3.time.scale()
      .range([0, width]);

  var y = d3.scale.linear()
      .range([height, 0]);

  var xAxis = d3.svg.axis()
      .scale(x)
      .orient("bottom");

  var yAxis = d3.svg.axis()
      .scale(y)
      .orient("left");

  
  var svg = d3.select(".activity-chart").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  data=d3.entries(activity);
  data.forEach(function(d) {
    d.key = parseDate(d.key);
  });
  data.sort(function(x,y){
      if (x.key>y.key){return 1;} 
      else if (x.key<y.key){return -1;}
      else return 0;});
  var timeDomain=(d3.extent(data, function(d) { return d.key; }))
  x.domain(timeDomain);
  y.domain([0,d3.max(data, function(d) { return d.value; })]);

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Changes");
 
 var line = d3.svg.line()
      .x(function(d) { return x(d.key); })
      .y(function(d) { return y(d.value); });
    
    var dataTest = d3.range(50).map(function(){return Math.random()*10})
    var testX = d3.scale.linear().domain([0, 10]).range([0, 700]);
    var testY = d3.scale.linear().domain([0, 10]).range([10, 290]);
    var testLine = d3.svg.line()
      .interpolate("cardinal")
      .x(function(d,i) {return testX(i);})
      .y(function(d) {return testY(d);})
    //pathTest = svg.append("svg:path").attr("d", testLine(dataTest));

  svg.append("path").attr("class", "line").attr("d", line(data));
  path = d3.select(".activity-chart").select("path");
  //renderDot(svg,path,data);
  renderTime(svg,data,x,y);
  
  $(".activity-chart").find("circle").on("click",function(event){
       var posX = event.pageX - $(".activity-chart").find("svg")[0].offsetLeft-100;
       var timestamp = x.invert(posX);
       var index = bisect(data, timestamp);
       var startDatum = data[index - 1];
       var endDatum = data[index];
       var range = endDatum.key - startDatum.key;
       if ((((timestamp-startDatum.key) % range) / range) > 0.5){
        index=index+1};
       selectedTime= data[index-1].key;
       
       location.href=("/artifacts?timestamp=" + selectedTime.toJSON().split("T")[0]);
        });
}
function renderTime(svg,data, scaleX, scaleY){
    var green=d3.rgb("#4682b4");
    var marker= 
        svg.append("circle")
          .attr("cx", 100)
          .attr("cy", 350)
          .attr("r", 5)
          .attr("fill", green)
          .on('mouseover', function(d){
            obj=d3.select(this);
            obj.attr("fill", green.brighter());
            obj.attr("r", 6);
            })
          .on("mouseout", function(d) {
            obj=d3.select(this);
            obj.attr("fill",green);
            obj.attr("r",5);
          });

        offsetLeft = $(".activity-chart").find("svg")[0].offsetLeft;
    // Add event listeners/handlers
    d3.select(".activity-chart").on('mouseover', function() {
      marker.style('display', 'inherit');
    }).on('mouseout', function() {
      marker.style('display', 'none');
    }).on('mousemove', function() {
      var mouse = d3.mouse(this);
      var posX=d3.event.pageX - offsetLeft-100;
      marker.attr('cx', posX);
        var timestamp = scaleX.invert(posX),
        index = bisect(data, timestamp),
        startDatum = data[index - 1],
        endDatum = data[index];
        if ((index-1)>=0 && index<=(data.length-1)){
        marker.style("display","inherit");
        interpolate = d3.interpolateNumber(startDatum.value, endDatum.value),
        range = endDatum.key - startDatum.key,
        valueY = interpolate(((timestamp-startDatum.key) % range) / range);

      marker.attr('cy', scaleY(valueY));}
        else { marker.style("display", "none")}
    });


}

function renderDot(svg,path,data)
{ 
    var circle = 
        svg.append("circle")
          .attr("cx", 100)
          .attr("cy", 350)
          .attr("r", 3)
          .attr("fill", "red");

    var pathEl = path.node();
    var pathLength = pathEl.getTotalLength();
    var BBox = pathEl.getBBox();
    var scale = pathLength/BBox.width;
    var offsetLeft = path[0][0].offsetLeft;
    offsetLeft = $(".activity-chart").find("svg")[0].offsetLeft;

    d3.select(".activity-chart").on("mousemove", function() {
      var x = d3.event.pageX - offsetLeft-100; 
      var beginning = x, end = pathLength, target;
      if (beginning <= 0 ) {
            return;
        }
      while (true) {
        
        target = Math.floor((beginning + end) / 2);
        pos = pathEl.getPointAtLength(target);
        if ((target === end || target === beginning) && pos.x !== x) {
            break;
        }
        if (pos.x > x)      end = target;
        else if (pos.x < x) beginning = target;
        else                break; //position found
      }
      circle
        .attr("opacity", 1)
        .attr("cx", x)
        .attr("cy", pos.y);
    });
 
}


