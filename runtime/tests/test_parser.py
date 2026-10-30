import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from specter_runtime.archaeology.parser import CodeParser

class TestCodeParser(unittest.TestCase):
    def setUp(self):
        self.parser = CodeParser()

    def test_python_parsing(self):
        source = """
import os
from typing import List

class DataProcessor:
    def process(self, item):
        pass

def test_pipeline():
    pass
"""
        analysis = self.parser.parse_source("src/processor.py", source)
        self.assertEqual(analysis.language, "python")
        self.assertEqual(len(analysis.imports), 2)
        self.assertTrue(analysis.has_tests)
        symbol_names = [s.name for s in analysis.symbols]
        self.assertIn("DataProcessor", symbol_names)
        self.assertIn("process", symbol_names)
        self.assertIn("test_pipeline", symbol_names)

    def test_rust_parsing(self):
        source = """
use std::sync::Arc;

pub struct Config {
    pub port: u16,
}

pub async fn run_server() {
}

#[test]
fn test_config() {}
"""
        analysis = self.parser.parse_source("backend/src/main.rs", source)
        self.assertEqual(analysis.language, "rust")
        self.assertEqual(len(analysis.imports), 1)
        self.assertTrue(analysis.has_tests)
        symbol_names = [s.name for s in analysis.symbols]
        self.assertIn("Config", symbol_names)
        self.assertIn("run_server", symbol_names)

    def test_typescript_parsing(self):
        source = """
import React from 'react';

export interface UserProps {
    id: string;
}

export function UserCard(props: UserProps) {
    return null;
}
"""
        analysis = self.parser.parse_source("frontend/src/Card.tsx", source)
        self.assertEqual(analysis.language, "typescript")
        symbol_names = [s.name for s in analysis.symbols]
        self.assertIn("UserProps", symbol_names)
        self.assertIn("UserCard", symbol_names)

if __name__ == "__main__":
    unittest.main()

