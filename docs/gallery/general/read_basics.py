"""
.. _reading_and_exploring_NWB_File:

Reading and Exploring an NWB File
==================================

This tutorial will demonstrate how to read, explore, and do basic visualizations with
an NWB File using different tools.

An :py:class:`~pynwb.file.NWBFile` represents a single session of an experiment.
It contains all the data of that session and the metadata required to understand the data.

We will demonstrate how to use the `DANDI <https://gui.dandiarchive.org/>`_ neurophysiology data archive to access
the data in two different ways: (1) by downloading it to your computer and (2) streaming it.

We will briefly show tools for exploring NWB Files interactively and refer the reader to the
:nwb_overview:`NWB Overview <tools/tools_home.html>` documentation for more details about the available tools.


.. seealso::
    You can learn more about the :py:class:`~pynwb.file.NWBFile` format in the :ref:`basics` tutorial.


The following examples will reference variables that may not be defined within the block they are used in. For
clarity, we define them here:
"""
# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_read_basics.png'
import numpy as np
from pynwb import NWBHDF5IO
import matplotlib.pyplot as plt

####################
# Read the data
# -------------
# We will use the `DANDI <https://gui.dandiarchive.org/>`_ neurophysiology data archive
# to access an NWB File. We will use data from one session of an experiment by
# `Chandravadia et al. (2020) <https://www.nature.com/articles/s41597-020-0415-9>`_, where
# the authors recorded single neuron activity from the medial temporal lobes of human subjects
# while they performed a recognition memory task.
#
# Download the data
# ^^^^^^^^^^^^^^^^^
# First, we will demonstrate how to download an NWB data file from `DANDI <https://gui.dandiarchive.org/>`_
# to your machine.
#
# 1. Go to the DANDI archive and open `this <https://gui.dandiarchive.org/dandiset/000004/draft>`_ dataset
# 2. List the files in this dataset by clicking the "Files" button in Dandiset Actions (top right column of the page).
#
# .. image:: ../../_static/demo_dandi_view_files_in_dataset.png
#   :width: 700
#   :alt: view files on dandi
#   :align: center
#
# 3. Choose the folder "sub-P11MHM" by clicking on its name.
#
# .. image:: ../../_static/demo_dandi_select_folder.png
#   :width: 700
#   :alt: selecting a folder on dandi
#   :align: center
#
# 4. Download the NWB data file "sub-P11HMH_ses-20061101_ecephys+image.nwb" to your
# computer by clicking on the download symbol.
#
# .. image:: ../../_static/demo_dandi_download_data.png
#   :width: 700
#   :alt: selecting a folder on dandi
#   :align: center
#
# Stream the data
# ^^^^^^^^^^^^^^^
#
# Next, we will demonstrate how to stream the data from the DANDI archive without
# having to download it to your machine.
# Streaming data requires having HDF5 installed with the ROS3 (read-only S3) driver.
# You can install from `conda-forge <https://conda-forge.org>`_ using ``conda``.
# You might need to first uninstall a currently installed version of ``h5py``.
#
# .. code-block:: bash
#
#    $ pip uninstall h5py
#    $ conda install -c conda-forge "h5py>=3.2"
#
# We can access the data stored in an S3 bucket using the DANDI API,
# which can be installed from pip:
#
# .. code-block:: bash
#
#    $ pip install -U dandi
#
# .. seealso::
#     You can learn more about streaming data in the :ref:`streaming` tutorial.
#
# Then, we will use the :py:class:`~dandi.dandiapi.DandiAPIClient` to obtain the S3 URL that points to the NWB File
# stored in S3. We will need the identifier of the dataset (``dandiset_id``) and the path
# to the NWB File.
# We can read these from the DANDI archive URL where ``dandiset_id`` is "000004" and
# file is located in "sub-P11HMH" folder.

from dandi.dandiapi import DandiAPIClient

dandiset_id = "000004"
filepath = "sub-P11HMH/sub-P11HMH_ses-20061101_ecephys+image.nwb"
with DandiAPIClient() as client:
    asset = client.get_dandiset(dandiset_id, "draft").get_asset_by_path(filepath)
    s3_path = asset.get_content_url(follow_redirects=1, strip_query=True)

####################
# Using NWBHDF5IO
# ---------------
#
# Reading and writing NWB data is carried out using the :py:class:`~pynwb.NWBHDF5IO` class.
# :py:class:`~pynwb.NWBHDF5IO` reads NWB data that is in the `HDF5 <https://www.hdfgroup.org/solutions/hdf5/>`_
# storage format, a popular, hierarchical format for storing large-scale scientific data.
#
# The first argument to the constructor of :py:class:`~pynwb.NWBHDF5IO` is the ``file_path`` -
# this can be the path that points to the downloaded file on your computer or
# it can be an S3 URL.
#
# Use the ``read`` method to read the data into a :py:class:`~pynwb.file.NWBFile` object.

# Open the file in read mode "r", and specify the driver as "ros3" for S3 files
io = NWBHDF5IO(s3_path, mode="r", driver="ros3")
nwbfile = io.read()

####################
# Access stimulus data
# --------------------
#
# Data representing stimuli that were presented to the experimental subject are stored in
# :py:class:`~pynwb.file.NWBFile.stimulus` within the :py:class:`~pynwb.file.NWBFile` object.

nwbfile.stimulus

####################
# ``NWBFile.stimulus`` is a dictionary that can contain PyNWB objects representing
# different types of data; such as images (grayscale, RGB) or time series of images.
# In this file, ``NWBFile.stimulus`` contains a single key "StimulusPresentation" with an
# :py:class:`~pynwb.image.OpticalSeries` object representing what images were shown to the subject and at what times.

nwbfile.stimulus["StimulusPresentation"]

####################
# .. code-block:: none
#
#     {'StimulusPresentation': StimulusPresentation pynwb.image.OpticalSeries at 0x140385583638560
#     Fields:
#       comments: no comments
#       conversion: 1.0
#       data: <HDF5 dataset "data": shape (200, 400, 300, 3), type "|u1">
#       description: no description
#       dimension: <HDF5 dataset "dimension": shape (3,), type "<i4">
#       distance: 0.7
#       field_of_view: <HDF5 dataset "field_of_view": shape (3,), type "<f8">
#       format: raw
#       interval: 1
#       orientation: lower left
#       resolution: -1.0
#       timestamps: <HDF5 dataset "timestamps": shape (200,), type "<f8">
#       timestamps_unit: seconds
#       unit: pixels
#     }
#
#
# Lazy loading of datasets
# ------------------------
# Data arrays are read passively from the NWB file.
# Accessing the ``data`` attribute of the :py:class:`~pynwb.image.OpticalSeries` object
# does not read the data values, but presents an HDF5 object that can be indexed to read data.
# You can use the ``[:]`` operator to read the entire data array into memory.

stimulus_presentation = nwbfile.stimulus["StimulusPresentation"]
all_stimulus_data = stimulus_presentation.data[:]

####################
# Images may be 3D or 4D (grayscale or RGB), where the first dimension must be time (frame).
# The second and third dimensions represent x and y.
# The fourth dimension represents the RGB value (length of 3) for color images.

stimulus_presentation.data.shape

####################
# .. code-block:: none
#
#     (200, 400, 300, 3)
#
# This :py:class:`~pynwb.image.OpticalSeries` data contains 200 images of size 400x300 pixels with three channels
# (red, green, and blue).
#
# Slicing datasets
# ----------------
# It is often preferable to read only a portion of the data.
# To do this, index or slice into the ``data`` attribute just like if you were
# indexing or slicing a numpy array.

frame_index = 31
image = stimulus_presentation.data[frame_index]
# Reverse the last dimension because the data were stored in BGR instead of RGB
image = image[..., ::-1]
plt.imshow(image, aspect="auto")

####################
#
# .. image:: ../../_static/demo_nwbfile_stimulus_plot_1.png
#   :width: 500
#   :alt: NWBFile stimulus image
#   :align: center
#
#
# Access single unit data
# -----------------------
# Data and metadata about sorted single units are stored in :py:class:`~pynwb.misc.Units`
# object. It stores metadata about each single unit in a tabular form, where each row represents
# a unit with spike times and additional metadata.
#
# .. seealso::
#     You can learn more about units in the :ref:`ecephys_tutorial` tutorial.
#

units = nwbfile.units

####################
# We can view the single unit data as a :py:class:`~pandas.DataFrame`.

units_df = units.to_dataframe()
units_df

####################
# To access the spike times of the first single unit, index :py:class:`~pynwb.file.NWBFile.units` with the column
# name "spike_times" and then the row index, 0. All times in NWB are stored in seconds
# relative to the session start time.

units["spike_times"][0]

####################
# .. code-block:: none
#
#     array([5932.811644, 6081.077044, 6091.982364, 6093.127644, 6095.068204,
#        6097.438244, 6116.694804, 6129.827604, 6134.825004, 6142.583924, ...])
#
#
# Visualize spiking activity relative to stimulus onset
# -----------------------------------------------------
# We can look at when these single units spike relative to when image stimuli were presented to the subject.
# We will iterate over the first 3 units and get their spike times.
# Then for each unit, we will iterate over each stimulus onset time and compute the spike times relative
# to stimulus onset. Finally, we will create a raster plot and histogram of these aligned spike times.

before = 1.0  # in seconds
after = 3.0

# Get the stimulus times for all stimuli
stim_on_times = stimulus_presentation.timestamps[:]

for unit in range(3):
    unit_spike_times = nwbfile.units["spike_times"][unit]
    trial_spikes = []
    for time in stim_on_times:
        # Compute spike times relative to stimulus onset
        aligned_spikes = unit_spike_times - time
        # Keep only spike times in a given time window around the stimulus onset
        aligned_spikes = aligned_spikes[
            (-before < aligned_spikes) & (aligned_spikes < after)
        ]
        trial_spikes.append(aligned_spikes)
    fig, axs = plt.subplots(2, 1, sharex="all")
    plt.xlabel("time (s)")
    axs[0].eventplot(trial_spikes)

    axs[0].set_ylabel("trial")
    axs[0].set_title("unit {}".format(unit))
    axs[0].axvline(0, color=[0.5, 0.5, 0.5])

    axs[1].hist(np.hstack(trial_spikes), 30)
    axs[1].axvline(0, color=[0.5, 0.5, 0.5])

####################
#
# .. image:: ../../_static/demo_nwbfile_units_plot.png
#   :width: 500
#   :alt: NWBFile units visualization
#   :align: center
#
# Access Trials
# -------------
# Trials are stored as :py:class:`~pynwb.epoch.TimeIntervals` object which is a subclass
# of :py:class:`~hdmf.common.table.DynamicTable`. :py:class:`~hdmf.common.table.DynamicTable` objects are used to store
# metadata about each trial in a tabular form, where each row represents a trial and has a start time, stop time,
# and additional metadata.
#
# .. seealso::
#     You can learn more about trials in the :ref:`basic_trials` tutorial section.
#
# Similarly to :py:class:`~pynwb.misc.Units`, we can view trials as a :py:class:`pandas.DataFrame`.

trials_df = nwbfile.trials.to_dataframe()
trials_df

####################
# The :py:class:`~pynwb.file.NWBFile.stimulus` can be mapped one-to-one to each row (trial)
# of :py:class:`~pynwb.file.NWBFile.trials` based on the ``stim_on_time`` column.

assert np.all(stimulus_presentation.timestamps[:] == trials_df.stim_on_time[:])

####################
# Visualize the first 3 images that were categorized as landscapes in the session:

stim_on_times_landscapes = trials_df[
    trials_df.category_name == "landscapes"
].stim_on_time
for time in stim_on_times_landscapes[:3]:
    img = np.squeeze(
        stimulus_presentation.data[
            np.where(stimulus_presentation.timestamps[:] == time)
        ]
    )
    # Reverse the last dimension because the data were stored in BGR instead of RGB
    img = img[..., ::-1]
    plt.figure()
    plt.imshow(img, aspect="auto")

####################
#
# .. image:: ../../_static/demo_nwbfile_stimulus_plot_2.png
#   :width: 500
#   :alt: NWBFile landscapes stimuli image
#   :align: center
#
# Exploring the NWB file
# ----------------------
# So far we have explored the NWB file by printing the :py:class:`~pynwb.file.NWBFile`
# object and accessing its attributes, but it may be useful to explore the data in a
# more interactive, visual way.
#
# You can use `NWBWidgets <https://github.com/NeurodataWithoutBorders/nwb-jupyter-widgets>`_,
# a package containing interactive widgets for visualizing NWB data,
# or you can use the `HDFView <https://www.hdfgroup.org/downloads/hdfview>`_
# tool, which can open any generic HDF5 file, which an NWB file is.
#
# NWBWidgets
# ^^^^^^^^^^
# Install NWBWidgets using pip install:
#
# .. code-block:: bash
#
#    $ pip install -U nwbwidgets
#
# Then import the ``nwbwidgets`` package and run the ``nwb2widget()`` function on
# the :py:class:`~pynwb.file.NWBFile` object.

#####################
#
# .. code-block:: python
#
#     from nwbwidgets import nwb2widget
#
#     nwb2widget(nwbfile)
#

####################
#
# .. image:: ../../_static/demo_nwbwidgets.png
#   :width: 700
#   :alt: inspect nwb file with nwbwidgets
#   :align: center
#
#
# HDFView
# ^^^^^^^
# To use `HDFView <https://www.hdfgroup.org/downloads/hdfview>`_ to inspect and explore the NWB file,
# download and install HDFView from `here <https://www.hdfgroup.org/downloads/hdfview>`_
# and then open the NWB file using the application.
#
# .. image:: ../../_static/demo_hdfview.png
#   :width: 700
#   :alt: inspect nwb file with hdfview
#   :align: center
#
