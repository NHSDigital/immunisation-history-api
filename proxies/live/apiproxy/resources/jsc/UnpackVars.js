function set_variables(location, vars) {

    if (typeof vars !== 'object') {
        return;
    }

    for (var key in vars)
    {
        if (!vars.hasOwnProperty(key))
            continue;
        variable = location + '.' + key;
        value = vars[key];
        if (typeof value === 'object' && value !== null) {
            set_variables(variable, value);
        }
        else {
            context.setVariable(variable, value);
        }
    }
}


var vars =  JSON.parse(context.getVariable("proxy.vars_raw"));
set_variables("apim.proxy", vars)
