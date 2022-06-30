var inProdEnvironment = context.getVariable('environment.name') === "prod";
var useStrictAuthorisedTargets = context.getVariable('app.use_strict_authorised_targets') == "true";

context.setVariable('apigee.USE_STRICT_AUTHORISED_TARGETS', useStrictAuthorisedTargets || inProdEnvironment);
