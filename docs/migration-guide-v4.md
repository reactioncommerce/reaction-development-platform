# Reaction v4.0.0

## Changes:

We are removing support for hydra and identity from the product that is being shipped by default. The auth APIs are now part of the GraphQL server and are implemented using [accounts-js](https://www.accountsjs.com/).
There is a new UI to handle login/signup and related functions. Instead of being redirected to the Identity page, users will be shown a modal.
Now instead of using `reaction-hydra` to validate the authentication token, we will be using [accounts-js](https://www.accountsjs.com/). Earlier, an API request was made to Hydra from the API-server to validate the token and return the associated user. This is now handled by the accounts-js APIs, which are bundled with the core APIs.

## Motivation:

Identity and Hydra were mostly introduced to enable OAuth 2 authentication and also to create a single service handling the authentication of both storefront and admin. But this also brought the task of maintaining these repos. The authentication was an overkill for developers who just wanted to get the service up and running. These services were very hard to deploy.

Starting 5 services doesn't seem user-friendly for a beginner. By reducing the number of services, we believe the product would become easier to use and extend. Also removing these services makes the software run faster and consume less memory on the machine.

Getting rid of Hydra and Identity reduces the footprint of Meteor in our application. This aligns with the target of getting rid of Meteor completely.

Also with our future plan to move to libraries providing UI layers for admin and storefront, we no more have the need for our own login service. We only need to provide the integration layer which is what this new structure would help with.

## Migration from v3.x.x:

This is a **BREAKING CHANGE**.

### If you want to upgrade to v4.x.x using account-js

- Users don't have to update their password. Their old credentials will work.
- Any "password reset" emails that were sent from `v3.x.x` would not work in `v4.x.x`. But the users can use `v4.x.x` to reset their passwords again.
- The `reaction-development-platform` will not start Hydra and Identity. If you are using any custom script to deploy/start these services, they are no longer needed.
- A new environment variable `STORE_URL` which points to the URL of the storefront is needed.
- A new environment variable `TOKEN_SECRET` which will be used to [hash the JWT token](https://www.accountsjs.com/docs/api/server/interfaces/accountsserveroptions/#tokensecret) should be added.
- All users will be logged out since their old token (created by Hydra) won't be recognized by `accounts-js`.

#### For users who have custom implementation of storefront:

You have to use [accounts-js](https://www.accountsjs.com/) to create a login/signup UI. A good example for that is [this PR](https://github.com/reactioncommerce/reaction-admin/pull/385/files) that adds the same functionality to storefront and admin.
**Note:** You have to encrypt the password before calling the API like [here](https://github.com/reactioncommerce/reaction-admin/pull/385/files#diff-8a6b10d412269cc540e290da1ce1eb94f2b481b0520daf916d47550fcb914c99R55) and [here](https://github.com/reactioncommerce/reaction-admin/pull/385/files#diff-b288f3325f14d44d0c915c764b6b94110cadb6ae6a170ad5453c184a01858ca1R3).

### If you want to upgrade to v4.x.x but keep using Hydra

This upgrade is not for you right now. Our suggestion would be to keep using `v3.x.x`. We will release the functionality to use any OAuth provider with `4.x.x` in the future. Please wait for that feature to make the upgrade.
