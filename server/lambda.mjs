import { SecretsManagerClient, GetSecretValueCommand } from '@aws-sdk/client-secrets-manager';
import { createHandler } from './server.mjs';
import { Auth } from './auth.mjs';
import { DynamoStore } from './dynamo-store.mjs';
import { bridge } from './lambda-bridge.mjs';

let ready;
async function initialize() {
  const origin = process.env.HODGE_ORIGIN;
  const secret = await new SecretsManagerClient({}).send(
    new GetSecretValueCommand({ SecretId: process.env.HODGE_APP_SECRET })
  );
  const appConfig = JSON.parse(secret.SecretString);
  const handler = await createHandler({
    root: process.env.LAMBDA_TASK_ROOT,
    origin,
    appConfig,
    auth: new Auth(origin, new DynamoStore(process.env.HODGE_SESSION_TABLE))
  });
  return bridge(handler);
}
export async function handler(event) {
  try {
    ready ||= initialize().catch((error) => {
      ready = null;
      throw error;
    });
    return await (
      await ready
    )(event);
  } catch {
    // Never emit OAuth URLs, tokens, credentials or request bodies to logs.
    return {
      statusCode: 503,
      headers: { 'Cache-Control': 'no-store', 'Content-Type': 'application/json' },
      body: JSON.stringify({
        error: 'The discussion service is temporarily unavailable. Please try again.'
      })
    };
  }
}
