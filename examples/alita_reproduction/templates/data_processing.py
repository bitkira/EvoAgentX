"""
Data Processing Script Template

This template provides a basic structure for data processing scripts.
Use this template to create scripts that load, process, and save data files.

Template Variables:
- input_file: Path to input data file
- output_file: Path to output data file  
- processing_description: Description of data processing operations
- additional_imports: Any additional imports needed
"""

#!/usr/bin/env python3

import pandas as pd
import numpy as np
import logging
import os
import sys
from typing import Dict, Any, Optional
{{additional_imports}}

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Data processing class for {{processing_description}}
    """
    
    def __init__(self, input_file: str, output_file: str):
        """
        Initialize the data processor.
        
        Args:
            input_file: Path to input data file
            output_file: Path to output data file
        """
        self.input_file = input_file
        self.output_file = output_file
        self.data = None
        logger.info(f"DataProcessor initialized: {input_file} -> {output_file}")
    
    def load_data(self) -> bool:
        """
        Load data from input file.
        
        Returns:
            True if data loaded successfully, False otherwise
        """
        try:
            logger.info(f"Loading data from: {self.input_file}")
            
            # Detect file type and load accordingly
            file_extension = os.path.splitext(self.input_file)[1].lower()
            
            if file_extension == '.csv':
                self.data = pd.read_csv(self.input_file)
            elif file_extension == '.json':
                self.data = pd.read_json(self.input_file)
            elif file_extension in ['.xlsx', '.xls']:
                self.data = pd.read_excel(self.input_file)
            else:
                logger.warning(f"Unsupported file type: {file_extension}")
                return False
            
            logger.info(f"Data loaded successfully. Shape: {self.data.shape}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return False
    
    def process_data(self) -> bool:
        """
        Process the loaded data.
        
        Returns:
            True if processing successful, False otherwise
        """
        try:
            if self.data is None:
                logger.error("No data loaded. Please load data first.")
                return False
            
            logger.info("Starting data processing...")
            
            # Data processing steps - customize based on requirements
            logger.info(f"Processing: {{processing_description}}")
            
            # Example processing operations (customize as needed):
            # 1. Data cleaning
            logger.info("Cleaning data...")
            self.data = self.data.dropna()  # Remove missing values
            
            # 2. Data transformation
            logger.info("Transforming data...")
            # Add your transformation logic here
            
            # 3. Data validation
            logger.info("Validating processed data...")
            if self.data.empty:
                logger.warning("Processed data is empty")
                return False
            
            logger.info(f"Data processing completed. Final shape: {self.data.shape}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return False
    
    def save_data(self) -> bool:
        """
        Save processed data to output file.
        
        Returns:
            True if data saved successfully, False otherwise
        """
        try:
            if self.data is None:
                logger.error("No processed data to save.")
                return False
            
            logger.info(f"Saving data to: {self.output_file}")
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            
            # Detect output file type and save accordingly
            file_extension = os.path.splitext(self.output_file)[1].lower()
            
            if file_extension == '.csv':
                self.data.to_csv(self.output_file, index=False)
            elif file_extension == '.json':
                self.data.to_json(self.output_file, orient='records', indent=2)
            elif file_extension in ['.xlsx', '.xls']:
                self.data.to_excel(self.output_file, index=False)
            else:
                logger.warning(f"Unsupported output file type: {file_extension}")
                return False
            
            logger.info("Data saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
            return False
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of processed data.
        
        Returns:
            Dictionary containing data summary
        """
        if self.data is None:
            return {"error": "No data available"}
        
        try:
            summary = {
                "shape": self.data.shape,
                "columns": list(self.data.columns),
                "data_types": self.data.dtypes.to_dict(),
                "memory_usage": self.data.memory_usage(deep=True).sum(),
                "missing_values": self.data.isnull().sum().to_dict()
            }
            
            # Add numeric summary if numeric columns exist
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                summary["numeric_summary"] = self.data[numeric_cols].describe().to_dict()
            
            return summary
            
        except Exception as e:
            return {"error": f"Error generating summary: {str(e)}"}


def main():
    """
    Main function to execute data processing workflow.
    """
    # Configuration
    input_file = "{{input_file}}"
    output_file = "{{output_file}}"
    
    # Validate input parameters
    if not os.path.exists(input_file):
        logger.error(f"Input file not found: {input_file}")
        sys.exit(1)
    
    # Initialize processor
    processor = DataProcessor(input_file, output_file)
    
    # Execute processing workflow
    try:
        # Step 1: Load data
        if not processor.load_data():
            logger.error("Failed to load data")
            sys.exit(1)
        
        # Step 2: Process data
        if not processor.process_data():
            logger.error("Failed to process data")
            sys.exit(1)
        
        # Step 3: Save processed data
        if not processor.save_data():
            logger.error("Failed to save processed data")
            sys.exit(1)
        
        # Step 4: Display summary
        summary = processor.get_summary()
        logger.info("Processing Summary:")
        for key, value in summary.items():
            if key != "numeric_summary":
                logger.info(f"  {key}: {value}")
        
        print("✅ Data processing completed successfully!")
        logger.info("Data processing workflow completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in main workflow: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()