"""Module for LLM integration using LangChain with Ollama."""

from functools import lru_cache
from typing import List, Optional, Dict, Any

from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

from .config import llm_config
from .exceptions import LLMError, ConfigurationError
from .logger import setup_logger

logger = setup_logger(__name__)

try:
    # Initialize Ollama with configured model
    llm = OllamaLLM(
        model=llm_config.model,
        base_url=f"http://{llm_config.host}" if llm_config.host else None,
        timeout=llm_config.timeout
    )
except Exception as e:
    logger.warning(f"Could not initialize Ollama. Make sure it's running locally. Error: {e}")
    llm = None

# Prompt templates
GENDER_DETECTION_TEMPLATE = """Analyze the character name and context to determine their likely gender.
Focus only on clear gender indicators and respond with only "female", "male", or "unknown".

Character Name: {character_name}
Context: {context}

Gender:"""

CONVERSATION_TOPIC_TEMPLATE = """Analyze this conversation to determine if it's primarily about men/male characters.
Consider mentions of men, male pronouns, and masculine terms.
Respond with only "true" if it's about men or "false" if it's not.

Conversation:
{dialogue}

Is this conversation primarily about men?"""

# Create prompt templates
gender_prompt = PromptTemplate(
    input_variables=["character_name", "context"],
    template=GENDER_DETECTION_TEMPLATE
)

topic_prompt = PromptTemplate(
    input_variables=["dialogue"],
    template=CONVERSATION_TOPIC_TEMPLATE
)

# Create modern runnable chains
if llm:
    gender_chain = (
        RunnableParallel({"prompt": gender_prompt})
        | {"response": RunnablePassthrough() | llm}
        | (lambda x: x["response"].strip().lower())
    )
    
    topic_chain = (
        RunnableParallel({"prompt": topic_prompt})
        | {"response": RunnablePassthrough() | llm}
        | (lambda x: x["response"].strip().lower() == "true")
    )
else:
    gender_chain = topic_chain = None

@lru_cache(maxsize=llm_config.cache_size)
def detect_gender(character_name: str, context: Optional[str] = None) -> str:
    """Detect character gender using LLM analysis.
    
    Args:
        character_name: Name of the character to analyze.
        context: Optional contextual information about the character.
        
    Returns:
        Gender as "female", "male", or "unknown".
        
    Raises:
        LLMError: If LLM analysis fails and no fallback is available.
    """
    if not llm:
        logger.warning("LLM not initialized, returning unknown gender")
        return "unknown"
        
    try:
        inputs: Dict[str, Any] = {
            "character_name": character_name,
            "context": context or f"Character named {character_name} in a script."
        }
        result = gender_chain.invoke(inputs)
        if result in ["female", "male", "unknown"]:
            return result
            
        logger.warning(f"Unexpected LLM gender result: {result}, defaulting to unknown")
        return "unknown"
    except Exception as e:
        logger.error(f"LLM gender detection failed for {character_name}: {e}")
        raise LLMError(f"Gender detection failed: {e}") from e

@lru_cache(maxsize=llm_config.cache_size)
def is_conversation_about_men(dialogue: List[str]) -> bool:
    """Determine if a conversation is primarily about men using LLM analysis.
    
    Args:
        dialogue: List of dialogue lines in the conversation.
        
    Returns:
        True if the conversation is primarily about men, False otherwise.
        
    Raises:
        LLMError: If LLM analysis fails and no fallback is available.
    """
    if not llm:
        logger.info("LLM not initialized, using heuristic analysis")
        return _heuristic_male_topic_detection(dialogue)
        
    try:
        inputs: Dict[str, Any] = {"dialogue": "\n".join(dialogue)}
        return topic_chain.invoke(inputs)
    except Exception as e:
        logger.error(f"LLM topic detection failed: {e}")
        logger.info("Falling back to heuristic analysis")
        return _heuristic_male_topic_detection(dialogue)

def _heuristic_male_topic_detection(dialogue: List[str]) -> bool:
    """Fallback method using simple heuristics to detect male-focused topics.
    
    Args:
        dialogue: List of dialogue lines to analyze.
        
    Returns:
        True if the conversation appears to be about men.
    """
    male_terms = {
        "he", "him", "his", "himself", "man", "men", "guy", "guys",
        "father", "brother", "son", "husband", "boyfriend"
    }
    text = " ".join(dialogue).lower()
    words = set(text.split())
    male_word_count = len(words.intersection(male_terms))
    return male_word_count > len(words) * 0.1

def validate_bechdel_result(
    female_characters: List[str],
    conversations: List[List[str]],
    original_result: bool
) -> bool:
    """Validate Bechdel test results using LLM analysis.
    
    Args:
        female_characters: List of female character names.
        conversations: List of conversations (each a list of dialogue lines).
        original_result: Original Bechdel test result to validate.
        
    Returns:
        Validated result (True if passes Bechdel test, False otherwise).
        
    Raises:
        ValidationError: If validation fails with no fallback available.
        ConfigurationError: If LLM is not properly configured.
    """
    if not llm:
        logger.warning("LLM not initialized, using original result")
        return original_result
        
    if not female_characters or len(female_characters) < 2:
        logger.info("Not enough female characters for Bechdel test")
        return False
        
    try:
        validation_prompt = f"""
        Validate if this script passes the Bechdel test:
        1. Has at least two named female characters: {', '.join(female_characters)}
        2. These women talk to each other
        3. Their conversation is not primarily about men

        Conversations:
        {chr(10).join(chr(10).join(conv) for conv in conversations)}

        Original analysis result: {"PASS" if original_result else "FAIL"}

        Respond with only "true" if the test passes or "false" if it fails.
        """
        
        result = llm.invoke(validation_prompt)
        validated = result.strip().lower() == "true"
        
        if validated != original_result:
            logger.info(
                f"LLM validation differs from original result: "
                f"original={original_result}, validated={validated}"
            )
            
        return validated
    except Exception as e:
        logger.error(f"LLM validation failed: {e}")
        raise ValidationError(f"Bechdel test validation failed: {e}") from e
