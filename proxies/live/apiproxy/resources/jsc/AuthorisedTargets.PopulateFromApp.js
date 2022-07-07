var flowVarPrefix = "apim-app-flow-vars.immunisation-history.authorised_targets";
var authorisedTargets = context.getVariable(flowVarPrefix);
// Either authorisedTargets is "*" OR it has been set as an array
if(authorisedTargets !== "*"){
    // If authorisedTargets has been set as an array then under the hood it has been flattened
    // into n objects 'path.to.object.0' to 'path.to.object.n', and there is no way to determine
    // the array length by inspection
    var index = 0;
    var _authorisedTargetsCollection = [];
    while(true){
        var flowVarName = flowVarPrefix.concat(".", index.toString());
        var _authorisedTarget = context.getVariable(flowVarName);
        if(_authorisedTarget === null){
            break;
        }
        _authorisedTargetsCollection.push(_authorisedTarget);
        index += 1;
    }
    authorisedTargets = _authorisedTargetsCollection.join(',');
}
// Note that any value other than an array or "*" will result in ""
context.setVariable('apigee.AUTHORISED_TARGETS', authorisedTargets);