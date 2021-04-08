jwksString = context.getVariable('jwks');
jwksObj = JSON.parse(jwksString);
kid = context.getVariable('jwt.DecodeJWT.FromExternalIdToken.decoded.header.kid');

jwksUpdated = false;

for (var i = 0; i < jwksObj.keys.length; i++) {
  if (kid == jwksObj.keys[i].kid) {
      jwksUpdated = true;
  }
}

context.setVariable('jwksUpdated', jwksUpdated);
