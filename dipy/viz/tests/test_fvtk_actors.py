import os
import numpy as np

from dipy.viz import actor, window

import numpy.testing as npt
from nibabel.tmpdirs import TemporaryDirectory
from dipy.tracking.streamline import center_streamlines, transform_streamlines
from dipy.align.tests.test_streamlinear import fornix_streamlines
from dipy.testing.decorators import xvfb_it

use_xvfb = os.environ.get('TEST_WITH_XVFB', False)
if use_xvfb == 'skip':
    skip_it = True
else:
    skip_it = False

run_test = (actor.have_vtk and
            actor.have_vtk_colors and
            window.have_imread and
            not skip_it)

if actor.have_vtk:
    if actor.major_version == 5 and use_xvfb:
        skip_slicer = True
        skip_surface = True
    else:
        skip_slicer = False
        skip_surface = False
else:
    skip_slicer = False
    skip_surface = False


@npt.dec.skipif(skip_slicer)
@npt.dec.skipif(not run_test)
@xvfb_it
def test_slicer():
    renderer = window.renderer()
    data = (255 * np.random.rand(50, 50, 50))
    affine = np.eye(4)
    slicer = actor.slicer(data, affine)
    slicer.display(None, None, 25)
    renderer.add(slicer)

    renderer.reset_camera()
    renderer.reset_clipping_range()
    # window.show(renderer)

    # copy pixels in numpy array directly
    arr = window.snapshot(renderer, 'test_slicer.png', offscreen=False)
    import scipy
    print(scipy.__version__)
    print(scipy.__file__)

    print(arr.sum())
    print(np.sum(arr == 0))
    print(np.sum(arr > 0))
    print(arr.shape)
    print(arr.dtype)

    report = window.analyze_snapshot(arr, find_objects=True)

    print(report)

    npt.assert_equal(report.objects, 1)
    # print(arr[..., 0])

    # The slicer can cut directly a smaller part of the image
    slicer.display_extent(10, 30, 10, 30, 35, 35)
    renderer.ResetCamera()

    renderer.add(slicer)

    # save pixels in png file not a numpy array
    with TemporaryDirectory() as tmpdir:
        fname = os.path.join(tmpdir, 'slice.png')
        # window.show(renderer)
        arr = window.snapshot(renderer, fname, offscreen=False)
        report = window.analyze_snapshot(fname, find_objects=True)
        npt.assert_equal(report.objects, 1)

    npt.assert_raises(ValueError, actor.slicer, np.ones(10))

    renderer.clear()

    rgb = np.zeros((30, 30, 30, 3))
    rgb[..., 0] = 1.
    rgb_actor = actor.slicer(rgb)

    renderer.add(rgb_actor)

    renderer.reset_camera()
    renderer.reset_clipping_range()

    arr = window.snapshot(renderer, offscreen=False)
    report = window.analyze_snapshot(arr, colors=[(255, 0, 0)])
    npt.assert_equal(report.objects, 1)
    npt.assert_equal(report.colors_found, [True])

    lut = actor.colormap_lookup_table(scale_range=(0, 255),
                                      hue_range=(0.4, 1.),
                                      saturation_range=(1, 1.),
                                      value_range=(0., 1.))
    renderer.clear()
    slicer_lut = actor.slicer(data, lookup_colormap=lut)

    slicer_lut.display(10, None, None)
    slicer_lut.display(None, 10, None)
    slicer_lut.display(None, None, 10)

    slicer_lut2 = slicer_lut.copy()
    slicer_lut2.display(None, None, 10)
    renderer.add(slicer_lut2)

    renderer.reset_clipping_range()

    arr = window.snapshot(renderer, offscreen=False)
    report = window.analyze_snapshot(arr, find_objects=True)
    npt.assert_equal(report.objects, 1)

    renderer.clear()

    data = (255 * np.random.rand(50, 50, 50))
    affine = np.diag([1, 3, 2, 1])
    slicer = actor.slicer(data, affine, interpolation='nearest')
    slicer.display(None, None, 25)

    renderer.add(slicer)
    renderer.reset_camera()
    renderer.reset_clipping_range()

    arr = window.snapshot(renderer, offscreen=False)
    report = window.analyze_snapshot(arr, find_objects=True)
    npt.assert_equal(report.objects, 1)
    npt.assert_equal(data.shape, slicer.shape)

    renderer.clear()

    data = (255 * np.random.rand(50, 50, 50))
    affine = np.diag([1, 3, 2, 1])

    from dipy.align.reslice import reslice

    data2, affine2 = reslice(data, affine, zooms=(1, 3, 2),
                             new_zooms=(1, 1, 1))

    slicer = actor.slicer(data2, affine2, interpolation='linear')
    slicer.display(None, None, 25)

    renderer.add(slicer)
    renderer.reset_camera()
    renderer.reset_clipping_range()

    # window.show(renderer, reset_camera=False)
    arr = window.snapshot(renderer, offscreen=False)
    report = window.analyze_snapshot(arr, find_objects=True)
    npt.assert_equal(report.objects, 1)
    npt.assert_array_equal([1, 3, 2] * np.array(data.shape),
                           np.array(slicer.shape))

@npt.dec.skipif(skip_surface)
@npt.dec.skipif(not run_test)
@xvfb_it
def test_surface():

    #Render volume
    renderer = window.renderer()
    data = np.zeros((50, 50, 50))
    data[20:30,25,25]=1.
    data[25, 20:30, 25] = 1.
    affine = np.eye(4)
    surface = actor.surface_actor(data, affine,
                                  colors=np.array([1, 0, 1]),
                                  opacity=.5)
    renderer.add(surface)

    renderer.reset_camera()
    renderer.reset_clipping_range()
    #window.show(renderer)

    #Test binarization
    renderer2 = window.renderer()
    data2 = np.zeros((50, 50, 50))
    data2[20:30, 25, 25] = 1.
    data2[35:40, 25, 25] = 1.
    affine = np.eye(4)
    surface2 = actor.surface_actor(data2, affine,
                                  colors=np.array([0, 1, 1]),
                                  opacity=.5)
    renderer2.add(surface2)

    renderer2.reset_camera()
    renderer2.reset_clipping_range()
    #window.show(renderer2)

    arr = window.snapshot(renderer, 'test_surface.png', offscreen=False)
    arr2 = window.snapshot(renderer2, 'test_surface2.png', offscreen=False)

    report = window.analyze_snapshot(arr, find_objects=True)
    report2 = window.analyze_snapshot(arr2, find_objects=True)

    npt.assert_equal(report.objects, 1)
    npt.assert_equal(report2.objects, 2)

    print(report)


    #test on real streamlines using tracking example
    from dipy.data import read_stanford_labels
    from dipy.reconst.shm import CsaOdfModel
    from dipy.data import default_sphere
    from dipy.direction import peaks_from_model
    from dipy.tracking.local import ThresholdTissueClassifier
    from dipy.tracking import utils
    from dipy.tracking.local import LocalTracking
    from dipy.viz import fvtk
    from dipy.viz.colormap import line_colors


    hardi_img, gtab, labels_img = read_stanford_labels()
    data = hardi_img.get_data()
    labels = labels_img.get_data()
    affine = hardi_img.get_affine()

    white_matter = (labels == 1) | (labels == 2)

    csa_model = CsaOdfModel(gtab, sh_order=6)
    csa_peaks = peaks_from_model(csa_model, data, default_sphere,
                                 relative_peak_threshold=.8,
                                 min_separation_angle=45,
                                 mask=white_matter)

    classifier = ThresholdTissueClassifier(csa_peaks.gfa, .25)

    seed_mask = labels == 2
    seeds = utils.seeds_from_mask(seed_mask, density=[1, 1, 1], affine=affine)

    # Initialization of LocalTracking. The computation happens in the next step.
    streamlines = LocalTracking(csa_peaks, classifier, seeds, affine,
                                step_size=2)

    # Compute streamlines and store as a list.
    streamlines = list(streamlines)

    # Prepare the display objects.
    streamlines_actor = fvtk.line(streamlines, line_colors(streamlines))
    seedroi_actor = actor.surface_actor(seed_mask, affine, [0, 1, 1], 0.5)

    # Create the 3d display.
    r = fvtk.ren()
    r2 = fvtk.ren()
    fvtk.add(r, streamlines_actor)
    arr3 = window.snapshot(r, 'test_surface3.png', offscreen=False)
    report3 = window.analyze_snapshot(arr3, find_objects=True)
    fvtk.add(r2, streamlines_actor)
    fvtk.add(r2, seedroi_actor)
    arr4 = window.snapshot(r2, 'test_surface4.png', offscreen=False)
    report4 = window.analyze_snapshot(arr4, find_objects=True)

    #assert that the seed ROI rendering isn't far away from the streamlines (affine error)
    npt.assert_equal(report3.objects,report4.objects)
    #fvtk.show(r)
    #fvtk.show(r2)





@npt.dec.skipif(not run_test)
@xvfb_it
def test_streamtube_and_line_actors():
    renderer = window.renderer()

    line1 = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2.]])
    line2 = line1 + np.array([0.5, 0., 0.])

    lines = [line1, line2]
    colors = np.array([[1, 0, 0], [0, 0, 1.]])
    c = actor.line(lines, colors, linewidth=3)
    window.add(renderer, c)

    c = actor.line(lines, colors, spline_subdiv=5, linewidth=3)
    window.add(renderer, c)

    # create streamtubes of the same lines and shift them a bit
    c2 = actor.streamtube(lines, colors, linewidth=.1)
    c2.SetPosition(2, 0, 0)
    window.add(renderer, c2)

    arr = window.snapshot(renderer)

    report = window.analyze_snapshot(arr,
                                     colors=[(255, 0, 0), (0, 0, 255)],
                                     find_objects=True)

    npt.assert_equal(report.objects, 4)
    npt.assert_equal(report.colors_found, [True, True])

    # as before with splines
    c2 = actor.streamtube(lines, colors, spline_subdiv=5, linewidth=.1)
    c2.SetPosition(2, 0, 0)
    window.add(renderer, c2)

    arr = window.snapshot(renderer)

    report = window.analyze_snapshot(arr,
                                     colors=[(255, 0, 0), (0, 0, 255)],
                                     find_objects=True)

    npt.assert_equal(report.objects, 4)
    npt.assert_equal(report.colors_found, [True, True])


@npt.dec.skipif(not run_test)
@xvfb_it
def test_bundle_maps():
    renderer = window.renderer()
    bundle = fornix_streamlines()
    bundle, shift = center_streamlines(bundle)

    mat = np.array([[1, 0, 0, 100],
                    [0, 1, 0, 100],
                    [0, 0, 1, 100],
                    [0, 0, 0, 1.]])

    bundle = transform_streamlines(bundle, mat)

    # metric = np.random.rand(*(200, 200, 200))
    metric = 100 * np.ones((200, 200, 200))

    # add lower values
    metric[100, :, :] = 100 * 0.5

    # create a nice orange-red colormap
    lut = actor.colormap_lookup_table(scale_range=(0., 100.),
                                      hue_range=(0., 0.1),
                                      saturation_range=(1, 1),
                                      value_range=(1., 1))

    line = actor.line(bundle, metric, linewidth=0.1, lookup_colormap=lut)
    window.add(renderer, line)
    window.add(renderer, actor.scalar_bar(lut, ' '))

    report = window.analyze_renderer(renderer)

    npt.assert_almost_equal(report.actors, 1)
    # window.show(renderer)

    renderer.clear()

    nb_points = np.sum([len(b) for b in bundle])
    values = 100 * np.random.rand(nb_points)
    # values[:nb_points/2] = 0

    line = actor.streamtube(bundle, values, linewidth=0.1, lookup_colormap=lut)
    renderer.add(line)
    # window.show(renderer)

    report = window.analyze_renderer(renderer)
    npt.assert_equal(report.actors_classnames[0], 'vtkLODActor')

    renderer.clear()

    colors = np.random.rand(nb_points, 3)
    # values[:nb_points/2] = 0

    line = actor.line(bundle, colors, linewidth=2)
    renderer.add(line)
    # window.show(renderer)

    report = window.analyze_renderer(renderer)
    npt.assert_equal(report.actors_classnames[0], 'vtkLODActor')
    # window.show(renderer)

    arr = window.snapshot(renderer)
    report2 = window.analyze_snapshot(arr)
    npt.assert_equal(report2.objects, 1)

    # try other input options for colors
    renderer.clear()
    actor.line(bundle, (1., 0.5, 0))
    actor.line(bundle, np.arange(len(bundle)))
    actor.line(bundle)
    colors = [np.random.rand(*b.shape) for b in bundle]
    actor.line(bundle, colors=colors)


if __name__ == "__main__":

    npt.run_module_suite()
