import React, { useEffect, useState } from "react";
import Amplify, { Auth } from "aws-amplify";
import { Authenticator } from "aws-amplify-react";
import styled from "@emotion/styled";

import Screens from "./components/Screens";
import amplifyConfig from "./config";

const Title = styled("h1")`
  text-align: center;
  text-transform: uppercase;
  color: #FF9900;
  margin-bottom: 8px;
`;

const theme = {
  formContainer: {
    margin: 0,
    padding: "8px 24px 24px"
  },
  formSection: {
    backgroundColor: "#232f3e",
    borderRadius: "4px"
  },
  sectionHeader: {
    color: "#FF9900"
  },
  sectionFooterSecondaryContent: {
    color: "#303952"
  },
  inputLabel: {
    color: "#FF9900"
  },
  input: {
    backgroundColor: "#f4f9f4",
    color: "#FF9900"
  },
  hint: {
    color: "#FF9900"
  },
  button: {
    borderRadius: "3px",
    backgroundColor: "#FF9900"
  },
  a: {
    color: "#FF9900"
  }
};

function App() {
  Amplify.configure({
    Auth: {
        region: amplifyConfig.apiGateway.REGION,
        userPoolId: amplifyConfig.cognito.USER_POOL_ID,
        userPoolWebClientId: amplifyConfig.cognito.APP_CLIENT_ID,
    },
    API: {
      endpoints: [
          {
              name: amplifyConfig.apiGateway.NAME,
              endpoint: amplifyConfig.apiGateway.URL
          },
      ]
    }
  });
  Auth.configure();

  const [state, setState] = useState({ isLoggedIn: false, user: null });

  const checkLoggedIn = () => {
    Auth.currentAuthenticatedUser()
      .then(data => {
        const user = { username: data.username, ...data.attributes };
        setState({ isLoggedIn: true, user });
      })
      .catch(error => console.log(error));
  };

  useEffect(() => {
    checkLoggedIn();
  }, []);

  return state.isLoggedIn ? (
    <Screens />
  ) : (
    <>
      <Title>Deequ - Data Quality Constraints</Title>
      <Authenticator
        onStateChange={authState => {
          if (authState === "signedIn") {
            checkLoggedIn();
          }
        }}
        theme={theme}
      />
    </>
  );
}

export default App;