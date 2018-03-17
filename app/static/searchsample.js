var samples = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
        url: '/search?autocomplete&term=%QUERY',
        wildcard: '%QUERY',
        transform: function(data) { return data.results; }
    }
});

function create_searchsample(searchfield) {
    searchfield.typeahead({
        minLength: 1,
        highlight: true
    }, {
        name: 'samples',
        display: function(result) { return result.name; },
        source: samples,
        templates: {
            suggestion: function(result) {
                if(result.parentname != '') {
                    parentinfo = '&nbsp;<i class="glyphicon glyphicon-level-up"></i>&nbsp;'+result.parentname
                } else {
                    parentinfo = ''
                }
                return '<div>'+
                       '<img src="/static/sample.png" width="24px" height="24px">'+result.name+
                       '&nbsp;<i class="glyphicon glyphicon-user"></i>&nbsp;'+result.ownername+
                       parentinfo+
                       '</div>';
            }
        }
    });
}

function create_selectsample(searchfield, hiddenfield, valid=true, placeholder="None") {
    searchfield.wrap("<div class=\"input-group\"></div>");
    searchfield.attr("placeholder", placeholder)

    var indicatorspan = $("<span class=\"input-group-addon\"></span>");
    var indicator = $("<i class=\"glyphicon glyphicon-"+(valid?"ok":"alert")+
                      "\" style=\"color:"+(valid?"green":"red")+";\"></i>");
    indicatorspan.append(indicator);
    searchfield.after(indicatorspan);

    searchfield.keyup(function(ev) {
        if(ev.keyCode == 13) return;
        if(searchfield.val() == '') {
            hiddenfield.attr('value', '');
            indicator.removeClass('glyphicon-alert');
            indicator.addClass('glyphicon-ok');
            indicator.css('color', 'green');
        } else {
            hiddenfield.attr('value', -1);
            indicator.removeClass('glyphicon-ok');
            indicator.addClass('glyphicon-alert');
            indicator.css('color', 'red');
        }
    });

    searchfield.bind('typeahead:select', function(ev, suggestion) {
        hiddenfield.attr('value', suggestion.id);
        indicator.removeClass('glyphicon-alert');
        indicator.addClass('glyphicon-ok');
        indicator.css('color', 'green');
    });

    create_searchsample(searchfield);
}