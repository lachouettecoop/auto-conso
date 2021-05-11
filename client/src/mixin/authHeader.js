function authHeader(token) {
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }
  return {};
}

export default authHeader;
