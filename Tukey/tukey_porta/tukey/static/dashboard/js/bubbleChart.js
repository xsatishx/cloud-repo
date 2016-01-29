
function bubbleChart(element, data){


}


$(document).ready(function(){



function createDataNodes(){
    var nodes = [{label:'project'},
    {label:'program'},
    {label:'center'},
    {label:'tissue_source_site'},
    {label:'portion'},
    {label:'aliquot'},
    {label:'protocol'},
    {label:

function createSystemNodes(){
    var nodes=[{label:'Sullivan'},
        {label:'Atwood'},
        {label:'Bionimbus-PDC'},
        {label:'skidmore'},
        {label:'OCC-Y'},
        {label:'Public Data Commons'}
        ]
    for （var i=0; i<269; i++){
        nodes.push({label:'node'})
    }
    var links=[]
    for (var i = 6;i<66;i++){
        links.push([0,i]);
    }
    for (var i = 66; i<89;i++){
        links.push([1,i]);
    }
    for (var i = 89; i<189;i++){
        links.push([2,i]);
    }
    for (var i = 189; i<214;i++){
        links.push([3,i]);
    }
    for (var i = 214; i<275;i++){
        links.push([4,i]);
    }
}
