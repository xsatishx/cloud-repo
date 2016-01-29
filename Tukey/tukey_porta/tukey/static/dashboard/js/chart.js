function BarChart(element, data){
    this.parent=d3.select(element[0]);
    var width=element.width();
    //width=500;
    this.keys=[]
    for (index in data)
        this.keys.push(data[index].key);
    this.values=[]
    for (index in data)
        this.values.push(data[index].value);
    //this.height=element.height();
    var barHeight=28;
    this.height=barHeight* data.length;
    this.svg=this.parent.append("svg").attr("width", width)
              .attr("height", this.height);
    var padding=300; 
    var x = d3.scale.linear().domain([0, 1])
            .range([5,width-padding]);

    //specify the y scales, with padding of 0.1 among bands
    var y = d3.scale.ordinal().rangeRoundBands([0,this.height],0.1).domain(this.keys);

    var yAxis = d3.svg.axis()
        .scale(y).orient("left");
    var titleWidth=width/5+60;
    this.bars= this.svg.selectAll("g").data(data).enter().append("g")
               .attr("transform", function(d, i){return "translate("
                 +titleWidth +"," + i* barHeight + ")";});
    this.bars.append("rect").attr("width",0)
             .attr("height", y.rangeBand())
             .transition().attr("width", function(d){return  x(d.value)})
                .duration(800);
   
    this.svg.append("g").
        attr("class","y axis").call(yAxis)
        .attr("transform", "translate(10,0)")
        .selectAll("text").style("text-anchor","inherit");
    $(".y.axis .tick").css("width",titleWidth);
    $(this.svg[0]).find("path").css("display","none");

    this.addText=function(){
        this.bars.append("text")
             .attr("x", function(d) { return x(d.value)+5})
             .attr("y", barHeight/2)
             .attr("text-anchor", "inherit")
             .attr("dy","0.25em")
             .attr("fill","#555")
             .text(function(d) {return d.text});
        
    }
    this.addColor = function(colorRange){
        var color=d3.scale.category10();
        var colors=["#c49c94","#f7b6d2","#bcbd22","#dbdb8d","#17becf","#9edae5"];
        this.svg.selectAll("rect").attr("fill",function(d,i){return colors[i]});
    }
}


$(document).ready(function(){
});
