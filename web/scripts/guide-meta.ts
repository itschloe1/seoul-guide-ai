export interface GuideMeta {
  title: string;
  description: string;
  category: string;
  categorySlug: string;
  order: number;
}

export const GUIDE_META: Record<string, GuideMeta> = {
  'banking/open-account': {
    title: 'How to Open a Bank Account in Korea as a Foreigner (2026)',
    description: 'Step-by-step guide to opening a Korean bank account, even without an ARC. Covers the phone-bank-ARC deadlock, KB vs Shinhan vs Hana comparison, restricted accounts, and online banking setup.',
    category: 'Banking & Finance',
    categorySlug: 'banking',
    order: 1,
  },
  'banking/cards-payments': {
    title: 'Korean Payment Guide: Cards, Kakao Pay & Sending Money Abroad',
    description: 'How to get a Korean credit card, use mobile payments (Kakao Pay, Naver Pay, WOWPASS), and send money home. Foreigner-friendly payment options explained.',
    category: 'Banking & Finance',
    categorySlug: 'banking',
    order: 2,
  },
  'daily-life/transportation': {
    title: 'Getting Around Korea: Subway, Bus, Taxi & KTX Guide for Foreigners',
    description: 'T-money cards, Seoul subway and bus system, taxi apps (Kakao T), KTX trains, intercity buses, and the best navigation apps for foreigners in Korea.',
    category: 'Daily Life',
    categorySlug: 'daily-life',
    order: 1,
  },
  'daily-life/delivery': {
    title: 'Food Delivery in Korea: How to Use Baemin, Coupang Eats & More',
    description: 'How to order food delivery in Korea as a foreigner. Baemin, Coupang Eats, Yogiyo setup guide. Parcel delivery, convenience store pickup, and dealing with delivery issues.',
    category: 'Daily Life',
    categorySlug: 'daily-life',
    order: 2,
  },
  'daily-life/utilities': {
    title: 'Utilities in Korea: Bills, Internet, Garbage & Recycling Guide',
    description: 'How to pay utility bills, set up internet, understand Korea\'s strict garbage and recycling rules, and manage heating costs as a foreigner.',
    category: 'Daily Life',
    categorySlug: 'daily-life',
    order: 3,
  },
  'daily-life/cost-of-living': {
    title: 'Cost of Living in Korea 2026: Monthly Budget Breakdown',
    description: 'How much does it cost to live in Korea? Detailed monthly budget for foreigners: housing, food, transport, utilities. Three budget tiers from 1.2M to 4M KRW. Seoul vs Busan vs smaller cities.',
    category: 'Daily Life',
    categorySlug: 'daily-life',
    order: 5,
  },
  'daily-life/phone-verification': {
    title: 'Korean Phone Verification: How to Get Past the Identity Wall',
    description: 'Korean identity verification (본인인증) explained for foreigners. SIM card options, phone number registration, and how to get past the verification requirement.',
    category: 'Daily Life',
    categorySlug: 'daily-life',
    order: 4,
  },
  'healthcare/find-hospital': {
    title: 'How to Find English-Speaking Doctors & Hospitals in Korea',
    description: 'Find hospitals and clinics with English-speaking staff in Korea. Emergency procedures, pharmacy guide, mental health resources, and key medical terms in Korean.',
    category: 'Healthcare',
    categorySlug: 'healthcare',
    order: 1,
  },
  'healthcare/insurance': {
    title: 'Korean Health Insurance (NHIS): Foreigner Enrollment Guide',
    description: 'How to enroll in Korea\'s National Health Insurance (NHIS) as a foreigner. Coverage, costs by income level, private insurance options, and how to claim benefits.',
    category: 'Healthcare',
    categorySlug: 'healthcare',
    order: 2,
  },
  'healthcare/pharmacy-essentials': {
    title: 'Korean Pharmacy Guide: Essential Medicines & OTC Products for Foreigners',
    description: 'What to buy at Korean pharmacies and convenience stores. Product names in Korean, prices, symptom phrases, 24-hour pharmacy locations, and an emergency kit shopping list under 25,000 KRW.',
    category: 'Healthcare',
    categorySlug: 'healthcare',
    order: 3,
  },
  'housing/find-apartment': {
    title: 'How to Find an Apartment in Korea: Apps, Agents & Prices (2026)',
    description: 'Finding housing in Korea as a foreigner. Best apps (Zigbang, Dabang), English-friendly platforms (Ziptoss, FOHO), real estate agents, costs by neighborhood, and viewing checklist.',
    category: 'Housing',
    categorySlug: 'housing',
    order: 1,
  },
  'housing/jeonse-wolse': {
    title: 'Jeonse vs Wolse: Korean Rental System Explained',
    description: 'Understanding Korea\'s unique jeonse (key money deposit) and wolse (monthly rent) systems. Deposit protection, fraud warning signs, legal rights, and contract red flags.',
    category: 'Housing',
    categorySlug: 'housing',
    order: 2,
  },
  'onboarding/arrival-checklist': {
    title: 'Moving to Korea Checklist: Your First 60 Days Step-by-Step',
    description: 'The exact order to set up your life in Korea: SIM card, ARC registration, bank account, phone plan, housing, and NHIS enrollment. Includes timelines and dependency chain.',
    category: 'Getting Started',
    categorySlug: 'onboarding',
    order: 1,
  },
  'onboarding/departure-checklist': {
    title: 'Leaving Korea Checklist: Pension Refund, Deposit & Taxes',
    description: 'Everything to handle before leaving Korea: national pension lump-sum refund (calculation examples), deposit recovery, tax settlement, severance pay, bank account, and ARC deregistration.',
    category: 'Getting Started',
    categorySlug: 'onboarding',
    order: 2,
  },
  'visa/arc-guide': {
    title: 'How to Get Your ARC Card in Korea: Step-by-Step Guide',
    description: 'How to apply for your Alien Registration Card (Residence Card) in Korea. Required documents, appointment booking, processing timeline, mobile ARC, and common issues.',
    category: 'Visa & Immigration',
    categorySlug: 'visa',
    order: 1,
  },
  'visa/visa-types': {
    title: 'Korean Visa Types Explained: E-2, D-2, F-1-D & More',
    description: 'All Korean visa types for foreigners: E-2 teaching, E-7 skilled worker, D-2 student, F-1-D digital nomad, F-6 marriage. How to switch visas, overstay fines, and address reporting rules.',
    category: 'Visa & Immigration',
    categorySlug: 'visa',
    order: 2,
  },
  'entertainment/kpop-concerts-tickets': {
    title: 'How to Buy K-Pop Concert Tickets in Korea as a Foreigner (2026)',
    description: 'Step-by-step guide to buying K-pop concert tickets on Interpark, Melon Ticket, YES24. Fan club presale, music show attendance, fansign lottery, and the 2AM cancelled ticket trick.',
    category: 'Entertainment',
    categorySlug: 'entertainment',
    order: 1,
  },
  'shopping/oliveyoung-guide': {
    title: 'Olive Young Shopping Guide 2026: Best K-Beauty Products for Foreigners',
    description: 'What to buy at Olive Young in Korea. Best sellers, steady sellers, trending ingredients (PDRN, exosomes), sunscreen rankings, tax refund tips, and price guide by category.',
    category: 'Shopping & K-Culture',
    categorySlug: 'shopping',
    order: 1,
  },
  'workplace/culture-communication': {
    title: 'Korean Workplace Culture: Nunchi, Hierarchy & Your Rights',
    description: 'How to navigate Korean workplace culture as a foreigner. Nunchi (눈치) explained, hierarchy rules, hoesik (회식) etiquette, dealing with discrimination, and your legal protections under Korean labor law.',
    category: 'Workplace',
    categorySlug: 'workplace',
    order: 1,
  },
};
