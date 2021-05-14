import amplifyConfig from "../config";
import {API, Auth} from "aws-amplify";

const APIGatewayName = amplifyConfig.apiGateway.NAME;
const suggestionsPath = '/suggestions';
const analyzersPath = '/analyzers';

async function getToken() {
    return (await Auth.currentSession()).getIdToken().getJwtToken()
}

async function getConstraint(type) {
    const token = await getToken();
    var path = (type.includes("suggestion")) ? suggestionsPath : analyzersPath
    const myInit = {
          headers: {
              Authorization: `Bearer ${token}`
          }
      };

      return API.get(APIGatewayName, path, myInit);
  }

async function createConstraint(type, input) {
    const token = await getToken();
    var path = (type.includes("suggestion")) ? suggestionsPath : analyzersPath
    const myInit = {
            body: input,
            headers: {
              Authorization: `Bearer ${token}`
            }
        };
        return API.post(APIGatewayName, path, myInit);
  }

async function updateConstraint(type, input) {
    const token = await getToken();
    var path = (type.includes("suggestion")) ? suggestionsPath : analyzersPath;
    const myInit = {
            body: input,
            headers: {
              Authorization: `Bearer ${token}`
            }
        };
        return API.put(APIGatewayName, path, myInit);
}

async function deleteConstraint(type, id) {
    const token = await getToken();
    var path = (type.includes("suggestion")) ? suggestionsPath : analyzersPath;
    const myInit = {
            headers: {
              Authorization: `Bearer ${token}`
            }
        };
        return API.del(APIGatewayName, path + '/' + id, myInit);
}

export default {getConstraint, createConstraint, updateConstraint, deleteConstraint}
