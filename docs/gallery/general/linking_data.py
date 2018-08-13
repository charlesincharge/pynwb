'''
Modular Data Storage using External Files
===========================================

PyNWB supports linking between files using external links.
'''

####################
# Example Use Case: Integrating data from multiple files
# ---------------------------------------------------------
#
# NBWContainer classes (e.g., :py:meth:`~pynwb.base.TimeSeries`) support the integration of data stored in external
# HDF5 files with NWB data files via external links. To make things more concrete, let's look at the following use
# case. We want to simultaneously record multiple data steams during data acquisition. Using the concept of external
# links allows us to save each data stream to an external HDF5 files during data acquisition and to
# afterwards link the data into a single NWB:N file. In this case, each recording becomes represented by a
# separate file-system object that can be set as read-only once the experiment is done.  In the following
# we are using :py:meth:`~pynwb.base.TimeSeries` as an example, but the same approach works for other
# NWBContainers as well.
#
#

####################
# .. tip::
#
#    The same strategies we use here for creating External Links also apply to Soft Links.
#    The main difference between soft and external links is that soft links point to other
#    objects within the same file while external links point to objects in external files.
#

####################
# .. tip::
#
#    In the case of :py:meth:`~pynwb.base.TimeSeries`, the uncorrected time  stamps generated  by the acquisition
#    system can be stored (or linked) in the *sync* group. In the NWB:N format, hardware-recorded time data
#    must then be corrected to a common time base (e.g., timestamps from all hardware sources aligned) before
#    it can be included in the *timestamps* of the *TimeSeries* This means, in the case
#    of :py:meth:`~pynwb.base.TimeSeries` we need to be careful that we are not including data with incompatible
#    timestamps in the same file when using external links.
#

####################
# .. warning::
#
#    External links can become stale/break. Since external links are pointing to data in other files
#    external links may become invalid any time files are modified on the file system, e.g., renamed,
#    moved or access permissions are changed.
#

####################
# Creating test data
# ---------------------------
#
# In the following we are creating 2 TimeSeries each written to a separate file. In the following we
# then show how we can integrate these files into a single NWBFile.


from datetime import datetime
from pynwb import NWBFile
from pynwb import TimeSeries
from pynwb import NWBHDF5IO
import numpy as np

# Create the base data
start_time = datetime(2017, 4, 3, 11, 0, 0)
create_date = datetime(2017, 4, 15, 12, 0, 0)
data = np.arange(1000).reshape((100, 10))
timestamps = np.arange(100)
filename1 = 'external1_example.nwb'
filename2 = 'external2_example.nwb'
filename3 = 'external_linkcontainer_example.nwb'
filename4 = 'external_linkdataset_example.nwb'

# Create the first file
nwbfile1 = NWBFile(source='PyNWB tutorial',
                   session_description='demonstrate external files',
                   identifier='NWBE1',
                   session_start_time=start_time,
                   file_create_date=create_date)
# Create the second file
test_ts1 = TimeSeries(name='test_timeseries1',
                      source='PyNWB tutorial',
                      data=data,
                      unit='SIunit',
                      timestamps=timestamps)
nwbfile1.add_acquisition(test_ts1)
# Write the first file
io = NWBHDF5IO(filename1, 'w')
io.write(nwbfile1)
io.close()

# Create the second file
nwbfile2 = NWBFile(source='PyNWB tutorial',
                   session_description='demonstrate external files',
                   identifier='NWBE2',
                   session_start_time=start_time,
                   file_create_date=create_date)
# Create the second file
test_ts2 = TimeSeries(name='test_timeseries2',
                      source='PyNWB tutorial',
                      data=data,
                      unit='SIunit',
                      timestamps=timestamps)
nwbfile2.add_acquisition(test_ts2)
# Write the second file
io = NWBHDF5IO(filename2, 'w')
io.write(nwbfile2)
io.close()


#####################
# Linking to select datasets
# --------------------------
#

####################
# Step 1: Create the new NWBFile
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

# Create the first file
nwbfile4 = NWBFile(source='PyNWB tutorial',
                   session_description='demonstrate external files',
                   identifier='NWBE4',
                   session_start_time=start_time,
                   file_create_date=create_date)


####################
# Step 2: Get the dataset you want to link to
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# Now let's open our test files and retrieve our timeseries.
#

# Get the first timeseries
io1 = NWBHDF5IO(filename1)
nwbfile1 = io1.read()
timeseries_1 = nwbfile1.get_acquisition('test_timeseries1')
timeseries_1_data = timeseries_1.data

####################
# Step 3: Create the object you want to link to the data
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# To link to the dataset we can simply assign the data object (here `` timeseries_1.data``) to a new ``TimeSeries``

# Create a new timeseries that links to our data
test_ts4 = TimeSeries(name='test_timeseries4',
                      source='PyNWB tutorial',
                      data=timeseries_1_data,   # <-------
                      unit='SIunit',
                      timestamps=timestamps)
nwbfile4.add_acquisition(test_ts4)

####################
# In the above case we did not make it explicit how we want to handle the data from
# our TimeSeries, this means that :py:class:`~pynwb.NWBHDF5IO` will need to
# determine on write how to treat the dataset. We can make this explicit and customize this
# behavior on a per-dataset basis by wrapping our dataset using
# :py:meth:`~pynwb.form.backends.hdf5.h5_utils.H5DataIO`

from pynwb.form.backends.hdf5.h5_utils import H5DataIO

# Create another timeseries that links to the same data
test_ts5 = TimeSeries(name='test_timeseries5',
                      source='PyNWB tutorial',
                      data=H5DataIO(data=timeseries_1_data,     # <-------
                                    link_data=True),            # <-------
                      unit='SIunit',
                      timestamps=timestamps)
nwbfile4.add_acquisition(test_ts5)

####################
# Step 4: Write the data
# ^^^^^^^^^^^^^^^^^^^^^^^
#
from pynwb import NWBHDF5IO

io4 = NWBHDF5IO(filename4, 'w')
io4.write(nwbfile4,
          link_data=True)     # <-------- Specify default behavior to link rather than copy data
io4.close()

#####################
# .. note::
#
#   In the case of TimeSeries one advantage of linking to just the main dataset is that we can now
#   use our own timestamps in case the timestamps in the original file are not aligned with the
#   clock of the NWBFile we are creating. In this way we can use the linking to "re-align" different
#   TimeSeries without having to copy the main data.


####################
# Linking to whole Containers
# ---------------------------
#
# Appending to files and linking is made possible by passing around the same
# :py:class:`~pynwb.form.build.map.BuildManager`. You can get a manager to pass around
# using the :py:meth:`~pynwb.get_manager` function.
#

from pynwb import get_manager

manager = get_manager()

####################
# .. tip::
#
#    You can pass in extensions to :py:meth:`~pynwb.get_manager` using the *extensions* argument.

####################
# Step 1: Get the container object you want to link to
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# Now let's open our test files and retrieve our timeseries.
#

# Get the first timeseries
io1 = NWBHDF5IO(filename1, manager=manager)
nwbfile1 = io1.read()
timeseries_1 = nwbfile1.get_acquisition('test_timeseries1')

# Get the second timeseries
io2 = NWBHDF5IO(filename2, manager=manager)
nwbfile2 = io2.read()
timeseries_2 = nwbfile2.get_acquisition('test_timeseries2')

####################
# Step 2: Add the container to another NWBFile
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# To intergrate both :py:meth:`~pynwb.base.TimeSeries` into a single file we simply create a new
# :py:meth:`~pynwb.file.NWBFile` and our existing :py:meth:`~pynwb.base.TimeSeries` to it. PyNWB's
# :py:meth:`~pynwb.NWBHDF5IO` backend then automatically detects that the TimeSeries have already
# been written to another file and will create external links for us.
#

# Create a new NWBFile that links to the external timeseries
nwbfile3 = NWBFile(source='PyNWB tutorial',
                   session_description='demonstrate external files',
                   identifier='NWBE3',
                   session_start_time=start_time,
                   file_create_date=create_date)
nwbfile3.add_acquisition(timeseries_1)             # <--------
nwbfile3.add_acquisition(timeseries_2)             # <--------

# Write our third file that includes our two timeseries as external links
io3 = NWBHDF5IO(filename3, 'w', manager=manager)
io3.write(nwbfile3)
io3.close()

####################
# Creating a single file for sharing
# -----------------------------------
#
# External links are convenient but to share data we may want to hand a single file with all the
# data to our collaborator rather than having to collect all relevant files. To do this,
# :py:class:`~pynwb.form.backends.hdf5.h5tools.HDF5IO` (and in turn :py:class:`~pynwb.NWBHDF5IO`)
# provide the convenience function :py:func:`~pynwb.form.backends.hdf5.h5tools.HDF5IO.copy_file`
