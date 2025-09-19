import Keycloak from "keycloak-js";

const baseUrl = (import.meta.env.VITE_KC_BASE_URL || "").replace(/\/+$/, "");

const keycloak = new Keycloak({
  url: baseUrl,
  realm: import.meta.env.VITE_KC_REALM,
  clientId: import.meta.env.VITE_KC_CLIENT_ID,
});

export default keycloak;
