import json
from pathlib import Path
from typing import Dict, Optional, List, Any
from utils.logger import Logger
from fastapi import HTTPException


class AspectsLoader:
    def __init__(self, versions_dir: str = 'resources/aspects'):
        self.logger = Logger().logger
        self.versions_dir = Path(versions_dir)
        self.versions: Dict[str, List[Dict]] = {}
        self.load_all_versions()

    def load_all_versions(self) -> None:
        """Load all available aspect versions from directory"""
        self.logger.info(f"Loading aspect versions from {self.versions_dir}")
        self.versions = {}

        if not self.versions_dir.exists():
            self.logger.warning(f"Versions directory {self.versions_dir} not found")
            return

        for path in self.versions_dir.glob('*.json'):
            try:
                version = path.stem
                with open(path, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                    data = self.normalize(raw_data)
                    self.versions[version] = data
                    self.logger.info(f"Loaded version {version} with {len(data)} entries")
            except Exception as e:
                self.logger.error(f"Failed to load {path}: {str(e)}", exc_info=True)

    def normalize(self, raw_data: Dict[str, Any]) -> List[Dict]:
        """Normalize raw JSON data into structured format"""
        normalized = []
        for name, aspects in raw_data.items():
            if not aspects:
                continue

            normalized_aspects = {
                aspect: details.get('amount', 0)
                for aspect, details in aspects.items()
            }

            if any(value != 0 for value in normalized_aspects.values()):
                normalized.append({
                    'name': name,
                    'aspects': normalized_aspects
                })
        return normalized

    def get_data(self, version: str) -> List[Dict]:
        """
        Get data for specific version

        Args:
            version: Version identifier (e.g., '2.7.4')

        Returns:
            List of aspect data entries

        Raises:
            HTTPException 404 if version not found
        """
        if version not in self.versions:
            self.logger.warning(f"Version {version} not found in available versions")
            raise HTTPException(
                status_code=404,
                detail=f"Version {version} not found. Available: {list(self.versions.keys())}"
            )
        return self.versions[version]

    def reload_version(self, version: Optional[str] = None) -> None:
        """
        Reload version data

        Args:
            version: Specific version to reload (None reloads all)

        Raises:
            HTTPException 500 if reload fails
        """
        self.logger.info(f"Reloading version: {version or 'ALL'}")
        try:
            if version:
                version_path = self.versions_dir / f"{version}.json"
                with open(version_path, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                    self.versions[version] = self.normalize(raw_data)
                    self.logger.info(f"Successfully reloaded version {version}")
            else:
                self.load_all_versions()
                self.logger.info("All versions reloaded successfully")
        except Exception as e:
            self.logger.error(f"Reload failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to reload data: {str(e)}"
            )

    def get_available_versions(self) -> List[str]:
        """Get sorted list of available versions"""
        return sorted(self.versions.keys())
