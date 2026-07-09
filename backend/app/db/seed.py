"""
Seed mock HCP profiles for demo purposes.
Idempotent — checks before inserting.
"""

from sqlalchemy import select
from app.db.session import async_session_factory
from app.models.db_models import HCPProfileModel

SEED_PROFILES = [
    {
        "name": "Dr. Priya Sharma",
        "specialty": "Oncology",
        "tier": "Tier 1",
        "last_interaction_sentiment": "Positive",
        "notes": "Key opinion leader in breast cancer research. Interested in OncoBoost Phase III data. Prefers evening meetings.",
    },
    {
        "name": "Dr. Rajesh Patel",
        "specialty": "Cardiology",
        "tier": "Tier 2",
        "last_interaction_sentiment": "Neutral",
        "notes": "Chief of cardiology at City Hospital. Open to clinical trial discussions. Prefers concise data summaries.",
    },
    {
        "name": "Dr. Sarah Chen",
        "specialty": "Neurology",
        "tier": "Tier 1",
        "last_interaction_sentiment": "Positive",
        "notes": "Leading researcher in Alzheimer's treatments. Very engaged with new compound data. Advisory board member.",
    },
    {
        "name": "Dr. Michael Smith",
        "specialty": "Endocrinology",
        "tier": "Tier 3",
        "last_interaction_sentiment": "Negative",
        "notes": "Concerned about side-effect profiles. Needs more real-world evidence before prescribing. Schedule follow-up with updated safety data.",
    },
    {
        "name": "Dr. Anika Desai",
        "specialty": "Pulmonology",
        "tier": "Tier 2",
        "last_interaction_sentiment": "Positive",
        "notes": "Interested in respiratory biologics. Active participant in CME programs. Requested samples of InhaleX.",
    },
    {
        "name": "Dr. James Wilson",
        "specialty": "Gastroenterology",
        "tier": "Tier 1",
        "last_interaction_sentiment": "Neutral",
        "notes": "Department head at University Medical Center. Evaluating GI-Shield for formulary inclusion. Data-driven decision maker.",
    },
    {
        "name": "Dr. Fatima Khan",
        "specialty": "Dermatology",
        "tier": "Tier 2",
        "last_interaction_sentiment": "Positive",
        "notes": "Early adopter of new dermatological treatments. Strong social media presence in medical community. Open to speaking engagements.",
    },
    {
        "name": "Dr. Robert Lee",
        "specialty": "Rheumatology",
        "tier": "Tier 3",
        "last_interaction_sentiment": None,
        "notes": "New contact — no prior interactions. Specializes in autoimmune conditions. Referred by Dr. Chen.",
    },
]


async def seed_hcp_profiles():
    """Insert seed HCP profiles if they don't already exist."""
    async with async_session_factory() as session:
        for profile_data in SEED_PROFILES:
            # Check if profile already exists
            result = await session.execute(
                select(HCPProfileModel).where(
                    HCPProfileModel.name == profile_data["name"]
                )
            )
            existing = result.scalar_one_or_none()

            if existing is None:
                profile = HCPProfileModel(**profile_data)
                session.add(profile)

        await session.commit()
        print(f"✅ Seeded {len(SEED_PROFILES)} HCP profiles (skipped existing)")
