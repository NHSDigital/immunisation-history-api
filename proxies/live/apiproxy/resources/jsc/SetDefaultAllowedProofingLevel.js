var allowedProofingLevel = context.getVariable('developer.app.nhs-login-allowed-proofing-level');

if (allowedProofingLevel === undefined || allowedProofingLevel === "") {
    context.setVariable('developer.app.nhs-login-allowed-proofing-level', 'P9');
}
