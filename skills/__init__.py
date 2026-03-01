"""Agent Skills for Personal AI Employee"""

SKILLS = [
    'process-email',
    'process-whatsapp',
    'create-plan',
    'execute-action',
    'request-approval',
    'generate-briefing',
    'audit-subscriptions'
]

def get_skill(name: str):
    """Get a skill module by name."""
    import importlib
    module_name = name.replace('-', '_')
    return importlib.import_module(f'skills.{module_name}.impl')
