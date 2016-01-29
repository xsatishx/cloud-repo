function makeid()
{
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < 7; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
}

function addChangeHandler(element){
    element.on('change.fortypeahead', function() {
    // Build a dictionary for the autocomplete    
    var thelement = $(this).parent().find('input')
    
    var autocomplete = thelement.typeahead({ minLength: 0, items: 25 });

    thelement.off('focus.fortypeahead');
    thelement.on('focus.fortypeahead', thelement.typeahead.bind(thelement, 'lookup'));                                                     

    autocomplete.data('typeahead').select = function () {
        var val = this.$menu.find('.active').attr('data-value');
        this.$element.val(val);
        generateQueryString();
        return this.hide();
    };

    // GLOBAL_DATA_SOURCE is defined in the template
    autocomplete.data('typeahead').source = GLOBAL_DATA_SOURCE[$(this).find(":selected").val()];
    }).change();
}

function generateQueryString() {

        function getCludeQuery(clude) {
            var cludeQuery = {};
            $(clude).find(".selection").each(function() {
                
                var attr = $(this).live('find',
                    '.attrSelect').find(":selected").val();

                var value = $(this).find('input').attr('value');
                if (typeof cludeQuery[attr] === 'undefined') {
                    cludeQuery[attr] = [];
                }
                cludeQuery[attr][cludeQuery[attr].length] = value;
            });
            return cludeQuery;
        }

        var includes = getCludeQuery("#include");
        var excludes = getCludeQuery("#exclude");

        function joinTerms(terms, innerJoinFunc, outerJoinFunc) {
            var count = 0;
            var queryString = [];
            $.each(terms, function(attr_name, outer_value) {
                var inner_queries = [];
                var inner_index = 0;
                $.each(outer_value, function(index, value) {
                    if (value) {
                     inner_queries[inner_index] = attr_name + ':' + '"' + value + '"';
                        inner_index++;
                    }
                });
                if (inner_queries.length > 0) {
                    queryString[count] = innerJoinFunc(inner_queries);
                    count++;
                }
            });
            queryString = outerJoinFunc(queryString);
            return queryString;
        }

        var includeString = joinTerms(includes, function(parts) {
            return "(" + parts.join(" OR ") + ")";
        }, function(parts) {
            return parts.join(" AND ");
        });

        var excludeString = joinTerms(excludes, function(parts) {
            return parts.join(" OR ");
        }, function(parts) {
            return parts.join(" OR ");
        });

        var current_query = '';
        
        if (includeString && excludeString) {
            current_query = [includeString, "(" + excludeString + ")"].join(" AND NOT ");
        }
        else if (includeString) {
            current_query = includeString;
        }
        else if (excludeString) {
            current_query = "NOT ("+excludeString+")";
        }

        $("#generated_query").attr('value', current_query);

    }


var includeClone = $('#fieldSelect').clone(true)
includeClone.find(".queryValue").attr('id', makeid());
includeClone.appendTo($("#include"));
addChangeHandler(includeClone.find(".attrSelect"));

var excludeClone = $('#fieldSelect').clone(true)
excludeClone.find(".queryValue").attr('id', makeid());
excludeClone.appendTo($("#exclude"));
addChangeHandler(excludeClone.find(".attrSelect"));

$(".addTerm").live('click', function() {
    var newid = makeid();
    var fieldClone = $('#fieldSelect').clone(true);
    fieldClone.find(".queryValue").attr('id', newid);

    fieldClone.append(
        $("#removeParent").clone(true)
    ).appendTo($(this).parent().parent().find(".terms"));

    addChangeHandler(fieldClone.find(".attrSelect"));
});

$(".removeParent").live('click', function() {
    $(this).parent().remove();
    generateQueryString();
});

$(".queryValue").on('keyup', generateQueryString);


    
