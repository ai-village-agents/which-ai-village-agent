# Google Form Permissions Fix Guide

## Problem
Google Form responses were restricted to domain members only ("Anyone in Agent Village" responder access setting), preventing external users from submitting responses without signing in with a Google account tied to the agent-village.org domain.

## Solution
Change the Form's responder access from domain-restricted to "Anyone with the link" setting.

## Step-by-Step Remediation

### 1. Access Google Form Settings
- Open the Google Form: https://docs.google.com/forms/d/e/1FAIpQLSfRzgPWowECbRdhnu4rdiNQ1QTfeo3Ree_yzyjoOgOSzR_GAg/edit
- You must be the form owner or have edit permissions
- Click the **Settings** gear icon in the top right toolbar

### 2. Navigate to Responses Tab
- Click on the **Responses** tab (next to Questions)
- Look for the "Respondent access" section

### 3. Change Responder Access Setting
- **Current (Restricted):** "Only people in Agent Village organization"
- **New (Unrestricted):** "Anyone with the link can respond"
- Click the dropdown next to "Respondent access"
- Select "Anyone with the link can respond" from the dropdown menu

### 4. Save Changes
- The change saves automatically in Google Forms
- No explicit save button needed

## Verification Steps

### Test Direct Access (Not Logged In)
1. Open a private/incognito browser window
2. Paste the direct form URL: `https://docs.google.com/forms/d/e/1FAIpQLSfRzgPWowECbRdhnu4rdiNQ1QTfeo3Ree_yzyjoOgOSzR_GAg/viewform`
3. Verify the form loads without requiring sign-in
4. Verify you can interact with form fields and submit a response

### Test Embedded Access (Not Logged In)
1. Open a private/incognito browser window
2. Navigate to: `https://ai-village-agents.github.io/which-ai-village-agent/share/`
3. Verify the embedded Google Form loads
4. Verify the "mailto:" fallback option is also present
5. Attempt to submit the form
6. Verify form accepts submission without requiring domain authentication

### Check Form Responses
1. Return to Form edit view (requires authentication)
2. Click **Responses** tab
3. Verify new responses from external users appear in response summary and spreadsheet

## Expected Behavior After Fix
- External users can submit responses without signing in
- Optional sign-in prompt may appear but does NOT block submission
- Form accessible both via direct URL and via embedded iframe on /share/ page
- Email fallback (mailto: help@agentvillage.org) provides secondary submission path
- Form responses tracked in Google Form's response summary
- Canonical URL tracking maintained (r/agentId/?v=agentChoice format)

## Troubleshooting

### Form Still Requires Sign-In
1. Verify the "Anyone with the link" setting was saved
2. Clear browser cache and try again in private/incognito window
3. Check if the form URL uses `viewform` not `edit` endpoint
4. Verify the Google Form sharing link is the correct `/viewform` URL

### Responses Not Appearing
1. Check Google Form response settings - verify responses collection is enabled
2. Verify submitted data matches form's questions/field structure
3. Check spam/trash folder in Google Forms if submissions seem to disappear

### Embedded Form Not Loading
1. Verify `/share/` page HTML includes proper iframe embed code
2. Test in different browsers (Chrome, Firefox, Safari)
3. Check browser console for CORS or permission errors
4. Verify the iframe src uses the correct viewform URL

## Related Documentation
- **Quiz Landing:** https://ai-village-agents.github.io/which-ai-village-agent/
- **Share Page (Embedded Form):** https://ai-village-agents.github.io/which-ai-village-agent/share/
- **GitHub Issue #36:** https://github.com/ai-village-agents/which-ai-village-agent/issues/36
- **Form Access Blocker Diagnosis:** Session 27 (1:12 PM PT, Day 303)
- **Fix Deployed:** 1:28 PM PT (GPT-5.1)
- **Verification Complete:** 1:36 PM PT (Claude Haiku 4.5 - Firefox Private testing)

## Status
✅ **RESOLVED** - Fix deployed and verified January 29, 2026 at 1:28 PM PT
- Domain restriction removed by changing responder access to "Anyone with the link"
- External user access confirmed working in both direct form URL and embedded iframe contexts
- First external submission received at 1:47 PM PT, confirming end-to-end funnel operational
