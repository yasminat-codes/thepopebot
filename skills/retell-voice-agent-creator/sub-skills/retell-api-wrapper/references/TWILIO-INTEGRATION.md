# Twilio Integration Guide

How to connect Retell AI agents to Twilio phone numbers for inbound and outbound
calling.

---

## Overview

Retell agents can handle real phone calls through Twilio. You need a Twilio phone
number imported into Retell and assigned to an agent. Once configured, inbound calls
to that number are handled by the agent, and outbound calls use that number as the
caller ID.

## Prerequisites

| Requirement | Details |
|-------------|---------|
| Twilio account | Active account with phone numbers |
| Twilio phone number | A purchased number with voice capability |
| Retell account | With a deployed agent |

## Step 1: Get a Twilio Phone Number

If you do not already have a Twilio number:

1. Log into Twilio console at https://console.twilio.com
2. Navigate to **Phone Numbers > Manage > Buy a Number**
3. Select a number with voice capability
4. Purchase the number

Or via Twilio API:
```bash
curl -X POST "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_SID/IncomingPhoneNumbers.json" \
  -u "$TWILIO_SID:$TWILIO_AUTH_TOKEN" \
  -d "PhoneNumber=+14155551234"
```

## Step 2: Import Phone Number to Retell

Import the Twilio number into your Retell account:

1. Go to Retell dashboard > **Phone Numbers**
2. Click **Import Phone Number**
3. Enter the Twilio phone number, SID, and auth token
4. Retell configures the Twilio webhook automatically

The import process updates the Twilio number's voice webhook URL to point to
Retell's servers.

## Step 3: Assign Agent to Phone Number

After import, assign an agent to handle calls on that number:

1. In Retell dashboard > **Phone Numbers**
2. Click the imported number
3. Select the agent from the dropdown
4. Save

## Inbound Call Flow

Once configured, inbound calls follow this path:

1. Caller dials the Twilio number
2. Twilio sends the call to Retell (via configured webhook)
3. Retell connects the call to the assigned agent
4. Agent handles the conversation
5. Call data is stored and available via API

## Outbound Call Flow

Use the imported Twilio number as `from_number` in the create-phone-call API:

```bash
curl -s -X POST https://api.retellai.com/v2/create-phone-call \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from_number": "+14155551234",
    "to_number": "+14155555678",
    "agent_id": "agent_7890xyz"
  }'
```

The `from_number` must be a Twilio number that has been imported into Retell.

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Inbound calls not reaching agent | Webhook not configured | Re-import the number |
| Outbound call fails with 422 | from_number not imported | Import the number first |
| Call connects but no audio | Agent not assigned to number | Assign agent in dashboard |
| "Number already in use" error | Number imported to another Retell account | Release from other account first |

## Multiple Numbers

You can import multiple Twilio numbers and assign different agents to each:

- **Sales line**: +1-415-555-1111 assigned to Sales Agent
- **Support line**: +1-415-555-2222 assigned to Support Agent
- **Appointments**: +1-415-555-3333 assigned to Booking Agent

Each number independently routes to its assigned agent.
