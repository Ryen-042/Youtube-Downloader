"""
This module provides TUI functions and prompts.
"""
import questionary
from questionary import Choice, Style, Separator
from questionary.prompts.common import InquirerControl

custom_style = Style([
    ('question',    '#af00d7'),                     # question text
    ('instruction', '#0000ff'),                     # user instructions for select, rawselect, checkbox
    ('disabled',    'fg:#858585 italic'),           # disabled choices for select and checkbox prompts
    ('answer',      "bold fg:#223377"),             # submitted answer text behind the question
    ('pointer',     'fg:#673ab7 bold'),             # pointer used in select and checkbox prompts
    ('selected',    'fg:#cc5454'),                  # style for a selected item of a checkbox
    ('separator',   'fg:#cc5454 bold italic'),      # separator in lists
    
    ("normal1",     "bold #0000ff"),
    ("normal2",     "bold #af00d7"),
    ("warning1",    "bold #875f87"),
    ("warning2",    "bold red"),
    ("exists",      "bold #5fd700")
])


def generate_choices(choices_names: list[str], default_choice: int=None, values: list=None, shortcuts: list[str]=None) -> list[Choice]:
    """
    Description:
        Generate a list of `Choice` objects.
    ---
    Parameters:
        `choices_names` (`list[str]`)
            A list containing the names of the choices.
        
        `default_choice` (`int`)
            An index to a default choice from the provided `choices_names`.
        
        `values` (`list`)
            The values of the choices that will be returned when selected. Defaults to `choices_names`.
        
        `shortcuts` (`list[str]`)
            A list of one character to be used as shortcuts for the choices.
            Defaults to a list of number from `1` to `len(choices_names)`.
    ---
    Returns: `list[Choice]`.
    """
    return [Choice(title=[("class:normal2", choice_name)], checked=default_choice == i,
                   value=None if not values else values[i], shortcut_key=str(i+1) if not shortcuts else shortcuts[i])
            for i, choice_name in enumerate(choices_names)]


def issue_selection_question(message: str, choices_names: list[str], default_choice=0, values: list=None, shortcuts: list=None, shortcuts_instruction_msg: str=None):
    """
    Description:
        Prompt the user to select a choice and return its corresponding value.
    ---
    Parameters:
        `message` (`str`)
            A custom message to display as the prompt question.
            
        `choices_names` (`list[str]`)
            A list containing the names of the choices.
        
        `default_choice` (`int`)
            An index to a default choice from the provided `choices_names`.
        
        `values` (`list`)
            The values of the choices that will be returned when selected. Defaults to `choices_names`.
        
        `shortcuts` (`list[str]`)
            A list of one character to be used as shortcuts for the choices.
            Defaults to a list of number from `1` to `len(choices_names)`.
            
        `shortcuts_instruction_msg` (`str`)
            A message to display after the prompt question (for control hints and shortcuts).
    ---
    Returns:
        ("Any") => The corresponding value to the selected choice.
    """
    generated_choices = generate_choices(choices_names, default_choice, values, shortcuts)
    if not shortcuts_instruction_msg:
        shortcuts_instruction_msg = "(Use up/down arrows and number keys to navigate)"
    else: 
        shortcuts_instruction_msg = f"(Use up/down arrow keys and {shortcuts_instruction_msg} buttons to navigate)"
    
    output = questionary.select(message, choices=generated_choices, style=custom_style, qmark="➥", pointer="➤",
                                default=generated_choices[default_choice], use_shortcuts=True,
                                show_selected=False, use_indicator=False, instruction=shortcuts_instruction_msg).ask()
    return generated_choices[default_choice].value if output is None else output


def issue_yes_no_question(message: str, default_choice=0, values=[0, 1], choices_names=["No", "Yes"], shortcuts=["n", "y"]):
    """
    Description:
        Prompt the user to select from two choices and return the corresponding value to the selected choice.
    ---
    Parameters:
        `message` (`str`)
            A custom message to display as the prompt question.
        
        `default_choice` (`int`)
            An index to a default choice from the provided `choices_names`.
        
        `values` (`list`)
            The values of the choices that will be returned when selected. Defaults to `choices_names`.
        
        `choices_names` (`list[str]`)
            A list containing the names of the choices.
        
        `shortcuts` (`list[str]`)
            A list of one character to be used as shortcuts for the choices.
            Defaults to a list of number from `1` to `len(choices_names)`.
    ---
    Returns:
        ("Any") => The corresponding value to the selected choice.
    """
    shortcuts_help = ("UP/down" if not default_choice else "up/DOWN") + " arrows and "
    shortcuts_help += f"{str(shortcuts[0]).upper()}/{shortcuts[1]}" if not default_choice else f"{shortcuts[0]}/{str(shortcuts[1]).upper()}"
    return issue_selection_question(message, choices_names, default_choice, values, shortcuts, f"(Use {shortcuts_help} keys to navigate)")
