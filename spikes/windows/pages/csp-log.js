window.cspViolations = [];
document.addEventListener('securitypolicyviolation', function (e) {
  window.cspViolations.push(e.violatedDirective + ' ' + e.blockedURI);
});
