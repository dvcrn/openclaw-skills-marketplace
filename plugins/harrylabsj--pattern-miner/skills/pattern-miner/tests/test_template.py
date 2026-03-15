"""Tests for Pattern Miner template module."""

import pytest
import tempfile
import json
from pathlib import Path

from pattern_miner.template import TemplateGenerator, ScriptGenerator, GeneratedTemplate


class TestTemplateGenerator:
    """Test cases for TemplateGenerator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = TemplateGenerator(output_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generate_from_pattern(self):
        """Test generating template from pattern."""
        class MockPattern:
            hash = 'abc123'
            code = 'def test():\n    x = 1\n    return x'
            language = 'python'
            variables = ['x']
            count = 2
        
        pattern = MockPattern()
        template = self.generator.generate_from_pattern(pattern, name='test_template')
        
        assert template.name == 'test_template'
        assert template.language == 'python'
        assert len(template.variables) > 0
    
    def test_convert_to_jinja2(self):
        """Test converting code to Jinja2 template."""
        code = """
def process(data):
    result = []
    for item in data:
        result.append(item)
    return result
"""
        template = self.generator._convert_to_jinja2(code, 'python', ['data', 'result'])
        
        assert '{{' in template or 'var_' in template
    
    def test_generate_template_header(self):
        """Test generating template header."""
        header = self.generator._generate_template_header('python', ['var1', 'var2'])
        
        assert 'Template Variables' in header or 'var_' in header
    
    def test_extract_template_variables(self):
        """Test extracting variables from template."""
        template = "{{ var_0 }} + {{ var_1 }} = {{ var_2 }}"
        variables = self.generator._extract_template_variables(template)
        
        assert 'var_0' in variables
        assert 'var_1' in variables
        assert 'var_2' in variables
    
    def test_generate_description(self):
        """Test generating template description."""
        code = "def my_function():\n    pass"
        description = self.generator._generate_description(code, 'python')
        
        assert 'function' in description.lower() or 'template' in description.lower()
    
    def test_generate_usage_example(self):
        """Test generating usage example."""
        usage = self.generator._generate_usage_example('test', ['var1', 'var2'], 'python')
        
        assert 'test' in usage
    
    def test_save_template(self):
        """Test saving template to file."""
        template = GeneratedTemplate(
            name='test_template',
            content='{{ var_0 }}',
            language='python',
            variables=['var_0'],
            description='Test template'
        )
        
        path = self.generator.save_template(template, 'test.jinja2')
        
        assert Path(path).exists()
        assert Path(path).read_text() == '{{ var_0 }}'
    
    def test_save_template_metadata(self):
        """Test saving template metadata."""
        template = GeneratedTemplate(
            name='test_template',
            content='{{ var_0 }}',
            language='python',
            variables=['var_0'],
            description='Test template'
        )
        
        self.generator.save_template(template, 'test.jinja2')
        
        meta_path = Path(self.temp_dir) / 'test.jinja2.meta'
        assert meta_path.exists()
        
        metadata = json.loads(meta_path.read_text())
        assert metadata['name'] == 'test_template'
        assert metadata['language'] == 'python'
    
    def test_render_template(self):
        """Test rendering template with variables."""
        template = GeneratedTemplate(
            name='test',
            content='Hello {{ name }}!',
            language='python',
            variables=['name']
        )
        
        result = self.generator.render_template(template, {'name': 'World'})
        
        assert result == 'Hello World!'
    
    def test_save_all_templates(self):
        """Test saving all generated templates."""
        template = GeneratedTemplate(
            name='test',
            content='test',
            language='python',
            variables=[]
        )
        self.generator.templates = [template]
        
        paths = self.generator.save_all_templates()
        
        assert len(paths) == 1
        assert Path(paths[0]).exists()
    
    def test_clear_templates(self):
        """Test clearing generated templates."""
        self.generator.templates = [GeneratedTemplate(
            name='test',
            content='test',
            language='python',
            variables=[]
        )]
        
        self.generator.clear()
        
        assert len(self.generator.templates) == 0


class TestScriptGenerator:
    """Test cases for ScriptGenerator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = ScriptGenerator(output_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generate_from_commands(self):
        """Test generating script from commands."""
        commands = ['echo "Hello"', 'ls -la', 'pwd']
        
        script = self.generator.generate_from_commands(commands, name='test_script')
        
        assert '#!/bin/bash' in script
        assert 'echo "Hello"' in script
        assert 'ls -la' in script
        assert 'test_script' in script
    
    def test_script_has_error_handling(self):
        """Test that generated script has error handling."""
        commands = ['echo test']
        script = self.generator.generate_from_commands(commands)
        
        assert 'set -e' in script or 'trap' in script
    
    def test_save_script(self):
        """Test saving script to file."""
        script = "#!/bin/bash\necho test"
        
        path = self.generator.save_script(script, 'test.sh')
        
        assert Path(path).exists()
        assert Path(path).read_text() == script
    
    def test_script_is_executable(self):
        """Test that saved script is executable."""
        script = "#!/bin/bash\necho test"
        
        path = self.generator.save_script(script, 'test.sh')
        
        import os
        assert os.access(path, os.X_OK)
