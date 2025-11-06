"""
Main GUI Window for PyWhiFuN

Converted from MATLAB WhiFuN main GUI application.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
from pathlib import Path
import json
import webbrowser
from datetime import datetime

from ..preprocessing.core import WhiFuNPreprocessor
from ..network_analysis.clustering import create_functional_networks_kmeans
from ..quality_control.motion_qc import batch_motion_qc
from ..io.file_utils import validate_data_structure
from ..utils.validation import validate_file_path


class WhiFuNMainWindow:
    """
    Main GUI window for PyWhiFuN toolbox.
    
    This is the primary interface for the White matter Functional Networks
    (WhiFuN) toolbox, providing a comprehensive suite of tools for investigating
    brain functional connectivity in White Matter (WM) and Gray Matter (GM).
    
    Converted from MATLAB WhiFuN main GUI application.
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PyWhiFuN - White Matter Functional Networks Toolbox")
        self.root.geometry("1200x800")
        
        # Initialize variables
        self.output_folder = tk.StringVar()
        self.subject_folder = tk.StringVar()
        self.is_bids = tk.BooleanVar(value=True)
        self.all_folders_subjects = tk.BooleanVar(value=True)
        self.n_subjects = tk.StringVar(value="0")
        
        # Data structure variables
        self.intermediate_folder = tk.StringVar(value="")
        self.func_folder_name = tk.StringVar(value="func")
        self.anat_folder_name = tk.StringVar(value="anat")
        self.func_image_name = tk.StringVar(value="*bold.nii*")
        self.anat_image_name = tk.StringVar(value="*T1w.nii*")
        
        # Preprocessing parameters
        self.setup_preprocessing_params()
        
        # Network analysis parameters
        self.setup_network_params()
        
        # Initialize GUI
        self.setup_gui()
        self.show_welcome_message()
    
    def setup_preprocessing_params(self):
        """Initialize preprocessing parameters with defaults."""
        self.preproc_params = {
            'slice_timing': tk.BooleanVar(value=True),
            'motion_correction': tk.BooleanVar(value=True),
            'coregistration': tk.BooleanVar(value=True),
            'segmentation': tk.BooleanVar(value=True),
            'normalization': tk.BooleanVar(value=True),
            'smoothing': tk.BooleanVar(value=True),
            'nuisance_regression': tk.BooleanVar(value=True),
            'filtering': tk.BooleanVar(value=True),
            
            # Motion parameters
            'max_translation': tk.DoubleVar(value=2.0),
            'max_rotation': tk.DoubleVar(value=2.0),
            'max_fd': tk.DoubleVar(value=0.5),
            'mean_fd': tk.DoubleVar(value=0.2),
            'fd_threshold': tk.DoubleVar(value=0.2),
            
            # Smoothing parameters
            'smoothing_fwhm': tk.DoubleVar(value=6.0),
            
            # Filtering parameters
            'high_pass': tk.DoubleVar(value=0.01),
            'low_pass': tk.DoubleVar(value=0.1),
            
            # Segmentation thresholds
            'wm_threshold': tk.DoubleVar(value=0.7),
            'gm_threshold': tk.DoubleVar(value=0.7),
            'csf_threshold': tk.DoubleVar(value=0.7)
        }
    
    def setup_network_params(self):
        """Initialize network analysis parameters."""
        self.network_params = {
            'wm_k_min': tk.IntVar(value=2),
            'wm_k_max': tk.IntVar(value=10),
            'gm_k_min': tk.IntVar(value=2),
            'gm_k_max': tk.IntVar(value=10),
            'cv_folds': tk.IntVar(value=4),
            'num_replicates': tk.IntVar(value=10),
            'focus_mask': tk.BooleanVar(value=False),
            'focus_mask_path': tk.StringVar(value="")
        }
    
    def setup_gui(self):
        """Setup the main GUI layout."""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.setup_data_tab()
        self.setup_preprocessing_tab()
        self.setup_network_tab()
        self.setup_visualization_tab()
        self.setup_log_tab()
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_data_tab(self):
        """Setup the data configuration tab."""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="Data Setup")
        
        # Main frame with scrollbar
        canvas = tk.Canvas(data_frame)
        scrollbar = ttk.Scrollbar(data_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Folder selection section
        folder_frame = ttk.LabelFrame(scrollable_frame, text="Folder Selection", padding=10)
        folder_frame.pack(fill='x', padx=10, pady=5)
        
        # Output folder
        ttk.Label(folder_frame, text="Output Folder:").grid(row=0, column=0, sticky='w', pady=2)
        ttk.Entry(folder_frame, textvariable=self.output_folder, width=60).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(folder_frame, text="Browse", command=self.browse_output_folder).grid(row=0, column=2, padx=5, pady=2)
        
        # Subject data folder
        ttk.Label(folder_frame, text="Subject Data Folder:").grid(row=1, column=0, sticky='w', pady=2)
        ttk.Entry(folder_frame, textvariable=self.subject_folder, width=60).grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(folder_frame, text="Browse", command=self.browse_subject_folder).grid(row=1, column=2, padx=5, pady=2)
        
        # BIDS checkbox
        ttk.Checkbutton(folder_frame, text="BIDS Format", variable=self.is_bids, 
                       command=self.toggle_bids).grid(row=2, column=0, sticky='w', pady=5)
        
        # Data structure configuration
        self.data_structure_frame = ttk.LabelFrame(scrollable_frame, text="Data Structure Configuration", padding=10)
        self.data_structure_frame.pack(fill='x', padx=10, pady=5)
        
        self.setup_data_structure_widgets()
        
        # Subject selection
        subject_frame = ttk.LabelFrame(scrollable_frame, text="Subject Selection", padding=10)
        subject_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Checkbutton(subject_frame, text="All folders are subjects", 
                       variable=self.all_folders_subjects,
                       command=self.update_subject_count).grid(row=0, column=0, sticky='w', pady=2)
        
        ttk.Label(subject_frame, text="Number of subjects:").grid(row=1, column=0, sticky='w', pady=2)
        ttk.Label(subject_frame, textvariable=self.n_subjects).grid(row=1, column=1, sticky='w', pady=2)
        
        # Action buttons
        action_frame = ttk.Frame(scrollable_frame)
        action_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(action_frame, text="Run Data Check", command=self.run_data_check).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Update Subject Count", command=self.update_subject_count).pack(side='left', padx=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_data_structure_widgets(self):
        """Setup data structure configuration widgets."""
        # Clear existing widgets
        for widget in self.data_structure_frame.winfo_children():
            widget.destroy()
        
        if not self.is_bids.get():
            # Custom data structure
            ttk.Label(self.data_structure_frame, text="Intermediate Folder:").grid(row=0, column=0, sticky='w', pady=2)
            ttk.Entry(self.data_structure_frame, textvariable=self.intermediate_folder, width=30).grid(row=0, column=1, padx=5, pady=2)
            
            ttk.Label(self.data_structure_frame, text="Functional Folder Name:").grid(row=1, column=0, sticky='w', pady=2)
            ttk.Entry(self.data_structure_frame, textvariable=self.func_folder_name, width=30).grid(row=1, column=1, padx=5, pady=2)
            
            ttk.Label(self.data_structure_frame, text="Anatomical Folder Name:").grid(row=2, column=0, sticky='w', pady=2)
            ttk.Entry(self.data_structure_frame, textvariable=self.anat_folder_name, width=30).grid(row=2, column=1, padx=5, pady=2)
            
            ttk.Label(self.data_structure_frame, text="Functional Image Name:").grid(row=3, column=0, sticky='w', pady=2)
            ttk.Entry(self.data_structure_frame, textvariable=self.func_image_name, width=30).grid(row=3, column=1, padx=5, pady=2)
            
            ttk.Label(self.data_structure_frame, text="Anatomical Image Name:").grid(row=4, column=0, sticky='w', pady=2)
            ttk.Entry(self.data_structure_frame, textvariable=self.anat_image_name, width=30).grid(row=4, column=1, padx=5, pady=2)
        else:
            # BIDS format
            ttk.Label(self.data_structure_frame, text="Using BIDS format - no additional configuration needed").grid(row=0, column=0, pady=10)
    
    def setup_preprocessing_tab(self):
        """Setup the preprocessing configuration tab."""
        preproc_frame = ttk.Frame(self.notebook)
        self.notebook.add(preproc_frame, text="Preprocessing")
        
        # Create scrollable frame
        canvas = tk.Canvas(preproc_frame)
        scrollbar = ttk.Scrollbar(preproc_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Preprocessing steps
        steps_frame = ttk.LabelFrame(scrollable_frame, text="Preprocessing Steps", padding=10)
        steps_frame.pack(fill='x', padx=10, pady=5)
        
        steps = [
            ('slice_timing', 'Slice Timing Correction'),
            ('motion_correction', 'Motion Correction'),
            ('coregistration', 'Coregistration'),
            ('segmentation', 'Segmentation'),
            ('normalization', 'Normalization'),
            ('smoothing', 'Smoothing'),
            ('nuisance_regression', 'Nuisance Regression'),
            ('filtering', 'Temporal Filtering')
        ]
        
        for i, (param, label) in enumerate(steps):
            ttk.Checkbutton(steps_frame, text=label, 
                           variable=self.preproc_params[param]).grid(row=i//2, column=i%2, sticky='w', padx=10, pady=2)
        
        # Motion parameters
        motion_frame = ttk.LabelFrame(scrollable_frame, text="Motion Parameters", padding=10)
        motion_frame.pack(fill='x', padx=10, pady=5)
        
        motion_params = [
            ('max_translation', 'Max Translation (mm):', 0, 0),
            ('max_rotation', 'Max Rotation (degrees):', 0, 2),
            ('max_fd', 'Max Framewise Displacement (mm):', 1, 0),
            ('mean_fd', 'Mean FD Threshold (mm):', 1, 2),
            ('fd_threshold', 'FD Threshold for Exclusion (mm):', 2, 0)
        ]
        
        for param, label, row, col in motion_params:
            ttk.Label(motion_frame, text=label).grid(row=row, column=col, sticky='w', pady=2)
            ttk.Entry(motion_frame, textvariable=self.preproc_params[param], width=10).grid(row=row, column=col+1, padx=5, pady=2)
        
        # Other parameters
        other_frame = ttk.LabelFrame(scrollable_frame, text="Other Parameters", padding=10)
        other_frame.pack(fill='x', padx=10, pady=5)
        
        other_params = [
            ('smoothing_fwhm', 'Smoothing FWHM (mm):', 0, 0),
            ('high_pass', 'High-pass Filter (Hz):', 0, 2),
            ('low_pass', 'Low-pass Filter (Hz):', 1, 0),
            ('wm_threshold', 'WM Threshold:', 1, 2),
            ('gm_threshold', 'GM Threshold:', 2, 0),
            ('csf_threshold', 'CSF Threshold:', 2, 2)
        ]
        
        for param, label, row, col in other_params:
            ttk.Label(other_frame, text=label).grid(row=row, column=col, sticky='w', pady=2)
            ttk.Entry(other_frame, textvariable=self.preproc_params[param], width=10).grid(row=row, column=col+1, padx=5, pady=2)
        
        # Action buttons
        action_frame = ttk.Frame(scrollable_frame)
        action_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(action_frame, text="Run Preprocessing", command=self.run_preprocessing).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Load Parameters", command=self.load_preprocessing_params).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Save Parameters", command=self.save_preprocessing_params).pack(side='left', padx=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_network_tab(self):
        """Setup the network analysis tab."""
        network_frame = ttk.Frame(self.notebook)
        self.notebook.add(network_frame, text="Network Analysis")
        
        # WM Network parameters
        wm_frame = ttk.LabelFrame(network_frame, text="White Matter Networks", padding=10)
        wm_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(wm_frame, text="K Range Min:").grid(row=0, column=0, sticky='w', pady=2)
        ttk.Entry(wm_frame, textvariable=self.network_params['wm_k_min'], width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(wm_frame, text="K Range Max:").grid(row=0, column=2, sticky='w', pady=2)
        ttk.Entry(wm_frame, textvariable=self.network_params['wm_k_max'], width=10).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Button(wm_frame, text="Create WM-FN", command=self.create_wm_networks).grid(row=1, column=0, columnspan=2, pady=10)
        
        # GM Network parameters
        gm_frame = ttk.LabelFrame(network_frame, text="Gray Matter Networks", padding=10)
        gm_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(gm_frame, text="K Range Min:").grid(row=0, column=0, sticky='w', pady=2)
        ttk.Entry(gm_frame, textvariable=self.network_params['gm_k_min'], width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(gm_frame, text="K Range Max:").grid(row=0, column=2, sticky='w', pady=2)
        ttk.Entry(gm_frame, textvariable=self.network_params['gm_k_max'], width=10).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Button(gm_frame, text="Create GM-FN", command=self.create_gm_networks).grid(row=1, column=0, columnspan=2, pady=10)
        
        # Analysis parameters
        analysis_frame = ttk.LabelFrame(network_frame, text="Analysis Parameters", padding=10)
        analysis_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(analysis_frame, text="CV Folds:").grid(row=0, column=0, sticky='w', pady=2)
        ttk.Entry(analysis_frame, textvariable=self.network_params['cv_folds'], width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(analysis_frame, text="Replicates:").grid(row=0, column=2, sticky='w', pady=2)
        ttk.Entry(analysis_frame, textvariable=self.network_params['num_replicates'], width=10).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Checkbutton(analysis_frame, text="Use Focus Mask", 
                       variable=self.network_params['focus_mask']).grid(row=1, column=0, sticky='w', pady=2)
        
        ttk.Entry(analysis_frame, textvariable=self.network_params['focus_mask_path'], width=40).grid(row=1, column=1, columnspan=2, padx=5, pady=2)
        ttk.Button(analysis_frame, text="Browse", command=self.browse_focus_mask).grid(row=1, column=3, padx=5, pady=2)
    
    def setup_visualization_tab(self):
        """Setup the visualization tab."""
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="Visualization")
        
        # Display options
        display_frame = ttk.LabelFrame(viz_frame, text="Display Functional Networks", padding=10)
        display_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(display_frame, text="Display WM Networks", command=self.display_wm_networks).pack(side='left', padx=5, pady=5)
        ttk.Button(display_frame, text="Display GM Networks", command=self.display_gm_networks).pack(side='left', padx=5, pady=5)
        ttk.Button(display_frame, text="Create Network Plots", command=self.create_network_plots).pack(side='left', padx=5, pady=5)
        
        # Quality control
        qc_frame = ttk.LabelFrame(viz_frame, text="Quality Control", padding=10)
        qc_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(qc_frame, text="View Motion QC", command=self.view_motion_qc).pack(side='left', padx=5, pady=5)
        ttk.Button(qc_frame, text="View Registration QC", command=self.view_registration_qc).pack(side='left', padx=5, pady=5)
        ttk.Button(qc_frame, text="Generate QC Report", command=self.generate_qc_report).pack(side='left', padx=5, pady=5)
    
    def setup_log_tab(self):
        """Setup the log/output tab."""
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="Log")
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=30)
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Log control buttons
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(log_control_frame, text="Clear Log", command=self.clear_log).pack(side='left', padx=5)
        ttk.Button(log_control_frame, text="Save Log", command=self.save_log).pack(side='left', padx=5)
    
    def show_welcome_message(self):
        """Show welcome message and information."""
        welcome_msg = """
Welcome to PyWhiFuN - White Matter Functional Networks Toolbox

This GUI-based toolbox offers researchers a user-friendly suite of automated tools 
for investigating brain functional connectivity in White Matter (WM) and Gray Matter (GM).

Key Features:
• Fully automated preprocessing pipeline
• White matter and gray matter functional network creation
• Quality control and visualization tools
• BIDS and custom data structure support

Getting Started:
1. Select Output Folder and Subject Data Folder
2. Configure data structure (BIDS or custom)
3. Run Data Check to verify images
4. Configure preprocessing parameters
5. Run Preprocessing
6. Create functional networks (WM-FN and GM-FN)
7. Visualize and analyze results

For more information, visit: https://github.com/p-kowadkar/WhiFuN

Reference:
Pratik Jain, Andrew M. Michael, Pan Wang, Xin Di, Bharat Biswal; WhiFuN:
A toolbox to map the white matter functional networks of the human brain.
Imaging Neuroscience 2025; doi: https://doi.org/10.1162/IMAG.a.3
        """
        
        self.log_message(welcome_msg)
    
    def log_message(self, message):
        """Add message to log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_status(self, message):
        """Update status bar."""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    # Event handlers
    def browse_output_folder(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
            self.log_message(f"Output folder set to: {folder}")
    
    def browse_subject_folder(self):
        """Browse for subject data folder."""
        folder = filedialog.askdirectory(title="Select Subject Data Folder")
        if folder:
            self.subject_folder.set(folder)
            self.log_message(f"Subject folder set to: {folder}")
            self.update_subject_count()
    
    def browse_focus_mask(self):
        """Browse for focus mask file."""
        file_path = filedialog.askopenfilename(
            title="Select Focus Mask",
            filetypes=[("NIfTI files", "*.nii *.nii.gz"), ("All files", "*.*")]
        )
        if file_path:
            self.network_params['focus_mask_path'].set(file_path)
    
    def toggle_bids(self):
        """Toggle BIDS format configuration."""
        self.setup_data_structure_widgets()
        self.log_message(f"BIDS format: {'Enabled' if self.is_bids.get() else 'Disabled'}")
    
    def update_subject_count(self):
        """Update the subject count."""
        if not self.subject_folder.get():
            self.n_subjects.set("0")
            return
        
        try:
            subject_path = Path(self.subject_folder.get())
            if subject_path.exists():
                # Count subdirectories
                subdirs = [d for d in subject_path.iterdir() if d.is_dir()]
                self.n_subjects.set(str(len(subdirs)))
                self.log_message(f"Found {len(subdirs)} potential subjects")
            else:
                self.n_subjects.set("0")
                self.log_message("Subject folder does not exist")
        except Exception as e:
            self.n_subjects.set("0")
            self.log_message(f"Error counting subjects: {str(e)}")
    
    def run_data_check(self):
        """Run data integrity check."""
        if not self.output_folder.get() or not self.subject_folder.get():
            messagebox.showerror("Error", "Please select both output and subject folders")
            return
        
        self.update_status("Running data check...")
        self.log_message("Starting data check...")
        
        def data_check_thread():
            try:
                # Create data structure configuration
                data_config = {
                    'is_bids': self.is_bids.get(),
                    'intermediate_folder': self.intermediate_folder.get(),
                    'func_folder_name': self.func_folder_name.get(),
                    'anat_folder_name': self.anat_folder_name.get(),
                    'func_image_name': self.func_image_name.get(),
                    'anat_image_name': self.anat_image_name.get()
                }
                
                # Validate data structure
                results = validate_data_structure(
                    self.subject_folder.get(),
                    data_config
                )
                
                # Log results
                self.log_message("Data check completed!")
                self.log_message(f"Valid subjects: {results['valid_subjects']}")
                self.log_message(f"Invalid subjects: {results['invalid_subjects']}")
                
                if results['errors']:
                    self.log_message("Errors found:")
                    for error in results['errors']:
                        self.log_message(f"  - {error}")
                
                self.update_status("Data check completed")
                
            except Exception as e:
                self.log_message(f"Data check failed: {str(e)}")
                self.update_status("Data check failed")
        
        # Run in separate thread
        thread = threading.Thread(target=data_check_thread)
        thread.daemon = True
        thread.start()
    
    def run_preprocessing(self):
        """Run preprocessing pipeline."""
        if not self.output_folder.get() or not self.subject_folder.get():
            messagebox.showerror("Error", "Please select both output and subject folders")
            return
        
        self.update_status("Running preprocessing...")
        self.log_message("Starting preprocessing pipeline...")
        
        def preprocessing_thread():
            try:
                # Create preprocessor
                preprocessor = WhiFuNPreprocessor(
                    output_folder=self.output_folder.get(),
                    subject_folder=self.subject_folder.get()
                )
                
                # Set parameters
                params = {key: var.get() for key, var in self.preproc_params.items()}
                preprocessor.set_parameters(params)
                
                # Run preprocessing
                results = preprocessor.run_preprocessing()
                
                self.log_message("Preprocessing completed successfully!")
                self.log_message(f"Processed {len(results)} subjects")
                
                self.update_status("Preprocessing completed")
                
            except Exception as e:
                self.log_message(f"Preprocessing failed: {str(e)}")
                self.update_status("Preprocessing failed")
        
        # Run in separate thread
        thread = threading.Thread(target=preprocessing_thread)
        thread.daemon = True
        thread.start()
    
    def create_wm_networks(self):
        """Create white matter functional networks."""
        self.create_networks('WM')
    
    def create_gm_networks(self):
        """Create gray matter functional networks."""
        self.create_networks('GM')
    
    def create_networks(self, tissue_type):
        """Create functional networks for specified tissue type."""
        if not self.output_folder.get():
            messagebox.showerror("Error", "Please select output folder")
            return
        
        self.update_status(f"Creating {tissue_type} networks...")
        self.log_message(f"Starting {tissue_type} network creation...")
        
        def network_thread():
            try:
                # Get parameters
                if tissue_type == 'WM':
                    k_min = self.network_params['wm_k_min'].get()
                    k_max = self.network_params['wm_k_max'].get()
                else:
                    k_min = self.network_params['gm_k_min'].get()
                    k_max = self.network_params['gm_k_max'].get()
                
                # Create networks
                results = create_functional_networks_kmeans(
                    output_folder=os.path.join(self.output_folder.get(), 'Analysis', f'{tissue_type}_FN'),
                    tissue_type=tissue_type,
                    k_range=(k_min, k_max),
                    cv_folds=self.network_params['cv_folds'].get(),
                    num_replicates=self.network_params['num_replicates'].get()
                )
                
                self.log_message(f"{tissue_type} network creation completed!")
                self.log_message(f"Optimal K: {results['optimal_k']}")
                
                self.update_status(f"{tissue_type} networks created")
                
            except Exception as e:
                self.log_message(f"{tissue_type} network creation failed: {str(e)}")
                self.update_status(f"{tissue_type} network creation failed")
        
        # Run in separate thread
        thread = threading.Thread(target=network_thread)
        thread.daemon = True
        thread.start()
    
    def display_wm_networks(self):
        """Display white matter networks."""
        self.log_message("Opening WM network visualization...")
        # Implementation would open visualization window
    
    def display_gm_networks(self):
        """Display gray matter networks."""
        self.log_message("Opening GM network visualization...")
        # Implementation would open visualization window
    
    def create_network_plots(self):
        """Create network plots."""
        self.log_message("Creating network plots...")
        # Implementation would create various network plots
    
    def view_motion_qc(self):
        """View motion quality control results."""
        if not self.output_folder.get():
            messagebox.showerror("Error", "Please select output folder")
            return
        
        qc_folder = os.path.join(self.output_folder.get(), 'Quality_Control', 'Head_motion')
        if os.path.exists(qc_folder):
            # Open QC folder in file explorer
            if sys.platform == "win32":
                os.startfile(qc_folder)
            elif sys.platform == "darwin":
                os.system(f"open '{qc_folder}'")
            else:
                os.system(f"xdg-open '{qc_folder}'")
        else:
            messagebox.showwarning("Warning", "Motion QC folder not found. Run preprocessing first.")
    
    def view_registration_qc(self):
        """View registration quality control results."""
        if not self.output_folder.get():
            messagebox.showerror("Error", "Please select output folder")
            return
        
        qc_folder = os.path.join(self.output_folder.get(), 'Quality_Control', 'Coregistration')
        if os.path.exists(qc_folder):
            # Open QC folder in file explorer
            if sys.platform == "win32":
                os.startfile(qc_folder)
            elif sys.platform == "darwin":
                os.system(f"open '{qc_folder}'")
            else:
                os.system(f"xdg-open '{qc_folder}'")
        else:
            messagebox.showwarning("Warning", "Registration QC folder not found. Run preprocessing first.")
    
    def generate_qc_report(self):
        """Generate comprehensive QC report."""
        self.log_message("Generating QC report...")
        # Implementation would create comprehensive QC report
    
    def load_preprocessing_params(self):
        """Load preprocessing parameters from file."""
        file_path = filedialog.askopenfilename(
            title="Load Preprocessing Parameters",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    params = json.load(f)
                
                # Update parameters
                for key, value in params.items():
                    if key in self.preproc_params:
                        self.preproc_params[key].set(value)
                
                self.log_message(f"Parameters loaded from: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load parameters: {str(e)}")
    
    def save_preprocessing_params(self):
        """Save preprocessing parameters to file."""
        file_path = filedialog.asksaveasfilename(
            title="Save Preprocessing Parameters",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                params = {key: var.get() for key, var in self.preproc_params.items()}
                
                with open(file_path, 'w') as f:
                    json.dump(params, f, indent=2)
                
                self.log_message(f"Parameters saved to: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save parameters: {str(e)}")
    
    def clear_log(self):
        """Clear the log text."""
        self.log_text.delete(1.0, tk.END)
    
    def save_log(self):
        """Save log to file."""
        file_path = filedialog.asksaveasfilename(
            title="Save Log",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                
                self.log_message(f"Log saved to: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log: {str(e)}")
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def launch_gui():
    """Launch the PyWhiFuN GUI application."""
    app = WhiFuNMainWindow()
    app.run()


if __name__ == "__main__":
    launch_gui()