# Template Catalog

9 industry templates with pre-configured defaults. Each template serves as a
starting point that can be customized through the interview process.

## 1. Receptionist

| Setting | Default |
|---------|---------|
| **Description** | General-purpose front desk agent. Answers calls, routes inquiries, takes messages, provides business information. |
| **Default Voice** | Female, warm, American English (ElevenLabs) |
| **Default Humanization** | Level 6 — conversational fillers, warm pauses, backchannel |
| **Default Responsiveness** | 1 (balanced) |
| **Interruption Sensitivity** | 0.8 (responsive to caller interruptions) |
| **Conversation States** | greeting, inquiry_routing, information, message_taking, transfer, closing |
| **Post-Call Analysis** | caller_name, caller_phone, reason_for_call, action_taken, follow_up_needed |
| **Sample Greeting** | "Good morning, thank you for calling [Business Name]. This is [Agent Name], how can I help you today?" |
| **Sample Closing** | "Is there anything else I can help you with? Great, have a wonderful day!" |

## 2. Sales

| Setting | Default |
|---------|---------|
| **Description** | Outbound or inbound sales agent. Qualifies leads, handles objections, pitches products, books demos or closes deals. |
| **Default Voice** | Male or female, confident, energetic (ElevenLabs) |
| **Default Humanization** | Level 7 — strategic pauses, confident fillers ("absolutely"), active listening |
| **Default Responsiveness** | 0 (fast — sales needs quick rapport) |
| **Interruption Sensitivity** | 0.9 (let prospect speak freely) |
| **Conversation States** | greeting, rapport_building, discovery, qualification, pitch, objection_handling, closing, follow_up |
| **Post-Call Analysis** | lead_qualified, budget_range, timeline, decision_maker, objections_raised, next_steps, deal_stage |
| **Sample Greeting** | "Hey [Name], this is [Agent Name] from [Business Name]. How are you doing today?" |
| **Sample Closing** | "Awesome, I'll get that demo scheduled for you. You'll get a confirmation email shortly. Looking forward to showing you what we can do!" |

## 3. Support

| Setting | Default |
|---------|---------|
| **Description** | Customer support agent. Troubleshoots issues, answers FAQs, escalates complex problems, logs tickets. |
| **Default Voice** | Female, calm, patient (ElevenLabs or OpenAI) |
| **Default Humanization** | Level 5 — empathetic pauses, acknowledgment cues, patient tone |
| **Default Responsiveness** | 1 (balanced — need to listen carefully to issues) |
| **Interruption Sensitivity** | 0.7 (moderate — let customer vent but maintain flow) |
| **Conversation States** | greeting, issue_identification, troubleshooting, solution, escalation, ticket_creation, closing |
| **Post-Call Analysis** | issue_category, issue_severity, resolved, resolution_method, escalated, ticket_id, customer_sentiment |
| **Sample Greeting** | "Thank you for calling [Business Name] support. My name is [Agent Name]. I'm here to help — what's going on?" |
| **Sample Closing** | "I'm glad we could get that sorted out. If anything else comes up, don't hesitate to call back. Take care!" |

## 4. Appointment

| Setting | Default |
|---------|---------|
| **Description** | Appointment scheduling agent. Books, reschedules, and cancels appointments. Checks availability. |
| **Default Voice** | Female, efficient, friendly (OpenAI or ElevenLabs) |
| **Default Humanization** | Level 4 — light fillers, efficiency-focused |
| **Default Responsiveness** | 0 (fast — scheduling is transactional) |
| **Interruption Sensitivity** | 0.6 (moderate) |
| **Conversation States** | greeting, appointment_type, date_selection, time_selection, confirmation, rescheduling, cancellation, closing |
| **Post-Call Analysis** | appointment_type, date_booked, time_booked, patient_name, phone_number, new_or_existing, rescheduled, cancelled |
| **Sample Greeting** | "Hi, thanks for calling [Business Name]. I can help you schedule an appointment. Are you a new or existing patient?" |
| **Sample Closing** | "You're all set for [Date] at [Time]. We'll send you a reminder the day before. See you then!" |

## 5. Personal Assistant

| Setting | Default |
|---------|---------|
| **Description** | Executive or personal assistant. Manages calls, takes messages, provides information, handles scheduling. |
| **Default Voice** | Female, polished, articulate (ElevenLabs) |
| **Default Humanization** | Level 7 — sophisticated conversational style, thoughtful pauses |
| **Default Responsiveness** | 1 (balanced — needs to think before responding) |
| **Interruption Sensitivity** | 0.8 (responsive) |
| **Conversation States** | greeting, caller_identification, purpose, action, message_taking, scheduling, transfer, closing |
| **Post-Call Analysis** | caller_name, caller_organization, purpose, urgency_level, action_taken, message_content, follow_up |
| **Sample Greeting** | "Good afternoon, you've reached [Executive Name]'s office. This is [Agent Name]. How may I assist you?" |
| **Sample Closing** | "I'll make sure [Executive Name] gets your message. Is there anything else? Have a great day." |

## 6. Lead Qualifier

| Setting | Default |
|---------|---------|
| **Description** | Inbound lead qualification agent. Screens calls, asks qualification questions, routes hot leads to sales. |
| **Default Voice** | Female or male, professional, conversational (ElevenLabs) |
| **Default Humanization** | Level 6 — conversational, curious tone |
| **Default Responsiveness** | 0 (fast — don't lose the lead's attention) |
| **Interruption Sensitivity** | 0.8 (let leads talk) |
| **Conversation States** | greeting, company_identification, need_discovery, budget_qualification, timeline_check, decision_maker_check, routing, closing |
| **Post-Call Analysis** | company_name, company_size, budget_range, timeline, decision_maker, pain_points, lead_score, routed_to |
| **Sample Greeting** | "Thanks for your interest in [Business Name]! I'd love to learn a bit about your needs so I can connect you with the right person. Can I ask you a few quick questions?" |
| **Sample Closing** | "This sounds like a great fit. Let me connect you with [Sales Rep] who specializes in exactly this. One moment!" |

## 7. Survey

| Setting | Default |
|---------|---------|
| **Description** | Customer satisfaction survey agent. Conducts NPS, CSAT, or custom surveys via phone. |
| **Default Voice** | Female, neutral, pleasant (OpenAI) |
| **Default Humanization** | Level 3 — minimal fillers, efficient but warm |
| **Default Responsiveness** | 1 (balanced — give respondent time to think) |
| **Interruption Sensitivity** | 0.5 (moderate) |
| **Conversation States** | greeting, consent, question_1_through_N, open_feedback, thank_you, closing |
| **Post-Call Analysis** | nps_score, csat_score, responses[], open_feedback_text, survey_completed, drop_off_point |
| **Sample Greeting** | "Hi [Name], this is [Agent Name] from [Business Name]. We'd love to hear about your recent experience. Do you have about 3 minutes for a quick survey?" |
| **Sample Closing** | "Thank you so much for your feedback — it really helps us improve. Have a wonderful day!" |

## 8. Debt Collection

| Setting | Default |
|---------|---------|
| **Description** | Payment reminder and debt collection agent. Professional, compliant, empathetic. Follows FDCPA guidelines. |
| **Default Voice** | Male, calm, authoritative (ElevenLabs) |
| **Default Humanization** | Level 4 — professional pauses, measured tone, no casual fillers |
| **Default Responsiveness** | 1 (balanced — must listen to debtor carefully) |
| **Interruption Sensitivity** | 0.9 (must let debtor respond fully) |
| **Conversation States** | greeting, identity_verification, mini_miranda, balance_notification, payment_options, hardship_discussion, payment_arrangement, closing |
| **Post-Call Analysis** | identity_verified, balance_discussed, payment_promised, payment_amount, payment_date, hardship_claimed, dispute_filed, call_compliant |
| **Sample Greeting** | "Hello, may I speak with [Debtor Name]? This is [Agent Name] calling from [Business Name]. This is an attempt to collect a debt, and any information obtained will be used for that purpose." |
| **Sample Closing** | "Thank you for your time, [Name]. To confirm, we've arranged a payment of [Amount] on [Date]. You'll receive a confirmation. Have a good day." |
| **Compliance Notes** | Must include Mini Miranda disclosure. Must verify identity before discussing debt. Must respect cease-and-desist requests. Must offer dispute rights. |

## 9. Real Estate

| Setting | Default |
|---------|---------|
| **Description** | Real estate agent assistant. Handles property inquiries, schedules showings, qualifies buyers, provides listing info. |
| **Default Voice** | Female, enthusiastic, knowledgeable (ElevenLabs) |
| **Default Humanization** | Level 7 — enthusiastic, descriptive, engaging storytelling |
| **Default Responsiveness** | 0 (fast — capture buyer interest quickly) |
| **Interruption Sensitivity** | 0.8 (responsive to buyer questions) |
| **Conversation States** | greeting, property_inquiry, buyer_qualification, listing_details, showing_scheduling, neighborhood_info, follow_up, closing |
| **Post-Call Analysis** | property_interested_in, buyer_budget, pre_approved, timeline, current_living_situation, showing_scheduled, follow_up_needed |
| **Sample Greeting** | "Hi there! Thanks for calling about our listing on [Street Name]. I'm [Agent Name] — are you looking to schedule a showing, or do you have some questions about the property?" |
| **Sample Closing** | "Wonderful, I've got you down for a showing on [Date] at [Time]. [Agent Name] will meet you at the property. You're going to love it!" |

## Template Selection Logic

1. Match user's stated use case against template descriptions.
2. Match industry keywords against template names.
3. If multiple templates could work, prefer the one closest to the stated role.
4. If no template matches, use `receptionist` as the neutral base and customize.
5. Always tell the user which template was selected and why.
