export interface GuideMeta {
  title: string;
  description: string;
  category: string;
  categorySlug: string;
  order: number;
}

export const GUIDE_META: Record<string, GuideMeta> = {
  'banking/open-account': {
    title: 'Opening a Bank Account in Korea as a Foreigner',
    description: 'Step-by-step guide to opening a Korean bank account. Covers the phone-bank-ARC deadlock, bank comparisons, restricted accounts, online banking setup, and common problems.',
    category: 'Banking & Finance',
    categorySlug: 'banking',
    order: 1,
  },
  'banking/cards-payments': {
    title: 'Cards & Payments Guide for Foreigners in Korea',
    description: 'Korean credit and debit cards, mobile payments (Kakao Pay, Naver Pay, WOWPASS), international remittance options, and how the Korean payment system works.',
    category: 'Banking & Finance',
    categorySlug: 'banking',
    order: 2,
  },
  'daily-life/transportation': {
    title: 'Transportation Guide for Foreigners in Korea',
    description: 'T-money cards, Seoul subway and bus system, taxi apps, KTX trains, intercity buses, navigation apps, and transportation tips for foreigners.',
    category: 'Daily Life',
    categorySlug: 'daily-life',
    order: 1,
  },
  'daily-life/delivery': {
    title: 'Food Delivery in Korea: Foreigner\'s Guide',
    description: 'How to use Baemin, Coupang Eats, and Yogiyo for food delivery. Parcel delivery, convenience store pickup, and dealing with delivery issues.',
    category: 'Daily Life',
    categorySlug: 'daily-life',
    order: 2,
  },
  'daily-life/utilities': {
    title: 'Utilities & Daily Services Guide for Foreigners in Korea',
    description: 'Paying bills, garbage and recycling rules, internet and TV setup, heating systems, and essential daily services for foreigners in Korea.',
    category: 'Daily Life',
    categorySlug: 'daily-life',
    order: 3,
  },
  'daily-life/cost-of-living': {
    title: 'Cost of Living in Korea: Foreigner\'s Guide',
    description: 'Detailed monthly budget breakdown for foreigners in Korea. Housing, food, transport, utilities costs. Three budget tiers, Seoul vs other cities, salary expectations.',
    category: 'Daily Life',
    categorySlug: 'daily-life',
    order: 5,
  },
  'daily-life/phone-verification': {
    title: 'Phone & Identity Verification Guide for Foreigners',
    description: 'Korean identity verification (본인인증), SIM card registration, phone number options, and how to get past the verification wall as a foreigner.',
    category: 'Daily Life',
    categorySlug: 'daily-life',
    order: 4,
  },
  'healthcare/find-hospital': {
    title: 'Finding English-Speaking Doctors & Hospitals in Korea',
    description: 'How to find hospitals and clinics with English-speaking staff, emergency procedures, pharmacies, mental health resources, and medical terminology.',
    category: 'Healthcare',
    categorySlug: 'healthcare',
    order: 1,
  },
  'healthcare/insurance': {
    title: 'Health Insurance Guide for Foreigners in Korea',
    description: 'National Health Insurance (NHIS) enrollment, coverage details, costs, foreigner requirements, private insurance options, and claiming benefits.',
    category: 'Healthcare',
    categorySlug: 'healthcare',
    order: 2,
  },
  'housing/find-apartment': {
    title: 'Finding an Apartment in Korea as a Foreigner',
    description: 'How to find housing in Korea. Apps (Zigbang, Dabang), real estate agents, English-friendly platforms, costs by neighborhood, and apartment viewing checklist.',
    category: 'Housing',
    categorySlug: 'housing',
    order: 1,
  },
  'housing/jeonse-wolse': {
    title: 'Jeonse vs Wolse: Korean Rental System Explained',
    description: 'Understanding Korea\'s unique jeonse (key money deposit) and wolse (monthly rent) systems. Deposit protection, fraud warnings, legal rights, and contract guide.',
    category: 'Housing',
    categorySlug: 'housing',
    order: 2,
  },
  'onboarding/arrival-checklist': {
    title: 'Arrival Checklist: Your First 60 Days in Korea',
    description: 'Step-by-step timeline for your first 60 days in Korea. SIM card, ARC registration, bank account, phone plan, housing, and NHIS enrollment in the right order.',
    category: 'Getting Started',
    categorySlug: 'onboarding',
    order: 1,
  },
  'onboarding/departure-checklist': {
    title: 'Leaving Korea Checklist: What to Do Before You Go',
    description: 'Complete departure checklist: national pension refund, deposit recovery, tax settlement, bank account, phone contract, insurance, and ARC deregistration.',
    category: 'Getting Started',
    categorySlug: 'onboarding',
    order: 2,
  },
  'visa/arc-guide': {
    title: 'ARC (Residence Card) Guide for Foreigners in Korea',
    description: 'How to get your Alien Registration Card (Residence Card) in Korea. Application process, required documents, timeline, mobile ARC, and common issues.',
    category: 'Visa & Immigration',
    categorySlug: 'visa',
    order: 1,
  },
  'visa/visa-types': {
    title: 'Visa Types for Foreigners in Korea: Complete Guide',
    description: 'All Korean visa types explained: E-2 teaching, E-7 skilled worker, D-2 student, F-1-D digital nomad, F-6 marriage. Switching visas, overstay consequences, address reporting.',
    category: 'Visa & Immigration',
    categorySlug: 'visa',
    order: 2,
  },
  'workplace/culture-communication': {
    title: 'Korean Workplace Culture & Communication for Foreigners',
    description: 'Nunchi (눈치), hierarchy, hoesik (회식), indirect communication, dealing with discrimination, English teacher career paths, and your legal protections.',
    category: 'Workplace',
    categorySlug: 'workplace',
    order: 1,
  },
};
