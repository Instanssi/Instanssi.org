$.tablesorter.addParser({ 
    id: 'humanizedBytes', 
    is: function(s) { 
        var spaceindex = s.indexOf(" ");
        if(spaceindex == -1) return false;
        
        var sp = s.split(" ");
        if(sp.length != 2) return false;
        var value = parseFloat(sp[0])
        if(isNaN(value)) return false;

        if(sp[1] == "B") return true;
        if(sp[1] == "KB") return true;
        if(sp[1] == "MB") return true;
        if(sp[1] == "GB") return true;
        
        return false;
    }, 
    format: function(s) { 
        var sp = s.split(" ");
        var value = parseFloat(sp[0]);
        if(isNaN(value)) return $.tablesorter.formatFloat(0);
        
        var outval = 0;
        if(sp[1] == "B") outval = value;
        if(sp[1] == "KB") outval = value * 1024;
        if(sp[1] == "MB") outval = value * 1024 * 1024;
        if(sp[1] == "GB") outval = value * 1024 * 1024 * 1024;

        return $.tablesorter.formatFloat(outval);
    }, 
    type: 'numeric' 
}); 

$.tablesorter.addParser({ 
    id: 'fiDate', 
    is: function(s) { 
        var spaceindex = s.indexOf(" ");
        if(spaceindex == -1) return false;
        
        var dtsplit = s.split(" ");
        if(dtsplit.length != 2) return false;
        if(dtsplit[0].length != 10 || dtsplit[0].indexOf(".") == -1) return false;
        if(dtsplit[1].length < 5  || dtsplit[1].indexOf(":") == -1) return false;
        
        var dates = dtsplit[0].split(".");
        var times = dtsplit[1].split(":");
        
        if(dates.length != 3) return false;
        if(times.length < 2) return false;
        if(dates[2].length != 4) return false;
        
        return true;
    }, 
    format: function(s) { 
        var dtsplit = s.split(" ");
        var dates = dtsplit[0].split(".");
        var times = dtsplit[1].split(":");
        var s = (times.length == 3) ? times[2] : 0;
        var date = new Date(dates[2], dates[1], dates[0], times[0], times[1], s);
        return $.tablesorter.formatFloat(date.getTime());
    }, 
    type: 'numeric' 
}); 

$.tablesorter.addParser({ 
    id: 'fiDateFancy', 
    is: function(s) { 
        var spaceindex = s.indexOf(" ");
        if(spaceindex == -1) return false;
        
        var dtsplit = s.split(" ");
        if(dtsplit.length != 3) return false;
        if(dtsplit[0].length != 10 || dtsplit[0].indexOf(".") == -1) return false;
        if(dtsplit[1] != "klo.") return false;
        if(dtsplit[2].length < 5 || dtsplit[2].indexOf(":") == -1) return false;
        
        var dates = dtsplit[0].split(".");
        var times = dtsplit[2].split(":");
        
        if(dates.length != 3) return false;
        if(times.length < 2) return false;
        if(dates[2].length != 4) return false;

        return true;
    }, 
    format: function(s) { 
        var dtsplit = s.split(" ");
        var dates = dtsplit[0].split(".");
        var times = dtsplit[2].split(":");
        var s = (times.length == 3) ? times[2] : 0;
        var date = new Date(dates[2], dates[1]-1, dates[0], times[0], times[1], s, 0);
        return $.tablesorter.formatFloat(date.getTime());
    }, 
    type: 'numeric' 
}); 