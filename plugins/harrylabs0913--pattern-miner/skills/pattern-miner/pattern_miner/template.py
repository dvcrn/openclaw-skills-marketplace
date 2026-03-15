"""Template generator for creating reusable templates from detected patterns."""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Try to import Jinja2, but provide fallback
try:
    from jinja2 import Template, Environment, BaseLoader
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    # Create dummy classes for fallback
    class Template:
        def __init__(self, *args, **kwargs):
            pass
        def render(self, **kwargs):
            return ""
    
    class Environment:
        def __init__(self, *args, **kwargs):
            pass
        def from_string(self, template):
            return Template()
    
    class BaseLoader:
        pass


@dataclass
class GeneratedTemplate:
    """Represents a generated template."""
    name: str
    content: str
    language: str
    variables: List[str]
    description: str = ""
    usage_example: str = ""


class TemplateGenerator:
    """Generates reusable templates from code patterns."""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir
        self.env = Environment(loader=BaseLoader())
        self.templates: List[GeneratedTemplate] = []
        
    def generate_from_pattern(self, pattern, name: str = None) -> GeneratedTemplate:
        """Generate a template from a detected code pattern."""
        code = pattern.code
        language = pattern.language
        variables = pattern.variables or []
        
        # Create Jinja2 template
        template_content = self._convert_to_jinja2(code, language, variables)
        
        # Extract or generate variable names
        extracted_vars = self._extract_template_variables(template_content)
        
        # Generate description
        description = self._generate_description(code, language)
        
        # Generate usage example
        usage = self._generate_usage_example(name or "template", extracted_vars, language)
        
        template = GeneratedTemplate(
            name=name or f"pattern_{pattern.hash[:8]}",
            content=template_content,
            language=language,
            variables=extracted_vars,
            description=description,
            usage_example=usage
        )
        
        self.templates.append(template)
        return template
    
    def _convert_to_jinja2(self, code: str, language: str, variables: List[str]) -> str:
        """Convert code to Jinja2 template format."""
        template = code
        
        # Replace identified variables with Jinja2 placeholders
        for i, var in enumerate(variables[:10]):  # Limit to 10 variables
            placeholder = f"{{{{ var_{i} }}}}"
            # Replace variable assignments and usages
            template = re.sub(
                rf'\b{re.escape(var)}\b',
                placeholder,
                template
            )
        
        # Add template header
        header = self._generate_template_header(language, variables[:10])
        
        return header + template
    
    def _generate_template_header(self, language: str, variables: List[str]) -> str:
        """Generate a template header with variable documentation."""
        if language == 'python':
            header = "{# Template Variables:\n"
            for i, var in enumerate(variables):
                header += f"  var_{i}: {var}\n"
            header += "#}\n\n"
            return header
        elif language in ('shell', 'bash'):
            header = "{#\n"
            header += "Template Variables:\n"
            for i, var in enumerate(variables):
                header += f"  var_{i}: {var}\n"
            header += "#}\n\n"
            return header
        return ""
    
    def _extract_template_variables(self, template_content: str) -> List[str]:
        """Extract variable names from Jinja2 template."""
        pattern = r'\{\{\s*(\w+)\s*\}\}'
        matches = re.findall(pattern, template_content)
        return list(set(matches))
    
    def _generate_description(self, code: str, language: str) -> str:
        """Generate a description for the template."""
        lines = [l.strip() for l in code.split('\n') if l.strip()]
        
        if language == 'python':
            # Look for function or class definitions
            for line in lines[:5]:
                if line.startswith('def '):
                    func_name = line.split('(')[0].replace('def ', '')
                    return f"Python function template: {func_name}"
                elif line.startswith('class '):
                    class_name = line.split('(')[0].replace('class ', '').replace(':', '')
                    return f"Python class template: {class_name}"
        
        if language in ('shell', 'bash'):
            # Look for function definitions
            for line in lines[:5]:
                if '()' in line and '{' in line:
                    func_name = line.split('(')[0].strip()
                    return f"Shell function template: {func_name}"
        
        # Generic description
        first_line = lines[0] if lines else "Code block"
        return f"{language} template: {first_line[:50]}"
    
    def _generate_usage_example(self, name: str, variables: List[str], language: str) -> str:
        """Generate usage example for the template."""
        if language == 'python':
            example = f"# Usage:\n# from jinja2 import Environment, FileSystemLoader\n"
            example += f"# env = Environment(loader=FileSystemLoader('templates'))\n"
            example += f"# template = env.get_template('{name}.jinja2')\n"
            example += f"# result = template.render("
            if variables:
                example += ", ".join(f"{v}='value'" for v in variables[:3])
            example += ")\n"
            return example
        elif language in ('shell', 'bash'):
            example = f"# Usage:\n# jinja2 {name}.jinja2 "
            if variables:
                example += " ".join(f"{v}=value" for v in variables[:3])
            return example
        return f"# Render template: {name}"
    
    def generate_script_from_pattern(self, pattern, script_name: str = None) -> str:
        """Generate an executable shell script from a pattern."""
        commands = pattern.code.split('\n') if hasattr(pattern, 'code') else []
        
        script = "#!/bin/bash\n\n"
        script += "# Auto-generated script from detected pattern\n"
        script += f"# Pattern hash: {pattern.hash}\n"
        script += f"# Occurrences: {pattern.count}\n\n"
        
        # Add variable declarations
        if pattern.variables:
            script += "# Variables\n"
            for i, var in enumerate(pattern.variables[:10]):
                script += f"VAR_{i}=\"${{1:-default_{i}}}\"\n"
            script += "\n"
        
        # Add commands
        script += "# Commands\n"
        for cmd in commands:
            if cmd.strip():
                script += f"{cmd.strip()}\n"
        
        return script
    
    def save_template(self, template: GeneratedTemplate, filename: str = None) -> str:
        """Save a template to a file."""
        if not self.output_dir:
            raise ValueError("Output directory not set")
            
        output_path = Path(self.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if filename is None:
            filename = f"{template.name}.jinja2"
        
        file_path = output_path / filename
        file_path.write_text(template.content, encoding='utf-8')
        
        # Save metadata
        metadata = {
            'name': template.name,
            'language': template.language,
            'variables': template.variables,
            'description': template.description,
            'usage': template.usage_example
        }
        
        meta_path = output_path / f"{filename}.meta"
        import json
        meta_path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        
        return str(file_path)
    
    def save_all_templates(self) -> List[str]:
        """Save all generated templates."""
        paths = []
        for template in self.templates:
            path = self.save_template(template)
            paths.append(path)
        return paths
    
    def render_template(self, template: GeneratedTemplate, variables: Dict[str, Any]) -> str:
        """Render a template with given variables."""
        jinja_template = self.env.from_string(template.content)
        return jinja_template.render(**variables)
    
    def clear(self):
        """Clear all generated templates."""
        self.templates.clear()


class ScriptGenerator:
    """Generates automation scripts from command patterns."""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir
        
    def generate_from_commands(self, commands: List[str], name: str = "automation") -> str:
        """Generate a shell script from a list of commands."""
        script = "#!/bin/bash\n\n"
        script += f"# Auto-generated automation script: {name}\n"
        script += f"# Generated by Pattern Miner\n\n"
        script += "set -e  # Exit on error\n\n"
        
        # Add error handling
        script += "trap 'echo \"Error occurred at line $LINENO\"' ERR\n\n"
        
        # Add commands
        for i, cmd in enumerate(commands):
            if cmd.strip():
                script += f"# Step {i + 1}\n"
                script += f"{cmd.strip()}\n\n"
        
        script += "echo \"Script completed successfully\"\n"
        
        return script
    
    def save_script(self, content: str, filename: str) -> str:
        """Save a script to a file."""
        if not self.output_dir:
            raise ValueError("Output directory not set")
            
        output_path = Path(self.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        file_path = output_path / filename
        file_path.write_text(content, encoding='utf-8')
        file_path.chmod(0o755)  # Make executable
        
        return str(file_path)
