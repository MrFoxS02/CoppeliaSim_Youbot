import numpy as np
from matplotlib import pyplot as plt
import matplotlib.backend_bases
from zmqRemoteApi import RemoteAPIClient

global_path = []

client = RemoteAPIClient()
sim = client.getObject('sim')

fire = sim.getObject(f'/Shape')
f_x, f_y, z = sim.getObjectPosition(fire, -1)

wheelJoints = [-1, -1, -1, -1]  # front left, rear left, rear right, front right
wheelJoints[0] = sim.getObject('/youBot/rollingJoint_fl')
wheelJoints[1] = sim.getObject('/youBot/rollingJoint_rl')
wheelJoints[2] = sim.getObject('/youBot/rollingJoint_rr')
wheelJoints[3] = sim.getObject('/youBot/rollingJoint_fr')
wheelJoints_coords = [sim.getObjectPosition(wheel, -1)[:2] for wheel in wheelJoints]


def cuboids_parser(n):
    cuboids_description = [sim.getObject(f'/Cuboid_{i}') for i in range(n)]  # Генератор списков для считыва дескриптора
    cuboids_x_coords = [sim.getObjectPosition(xy, -1)[0] for xy in cuboids_description]  # x-я координата
    cuboids_y_coords = [sim.getObjectPosition(xy, -1)[1] for xy in cuboids_description]  # y-я координата
    return cuboids_x_coords, cuboids_y_coords


def prepare_vector_massiv_to_x_y_vector(vectors):  # ((x1, y1), (x2, y2)) -> x = [x1, x2 ...], y = [y1, y2 ...]
    x = [_[0] for _ in vectors]
    y = [_[1] for _ in vectors]
    return x, y


def edge_room_descritesation(x, y):  # Вершины комнаты
    room_vectors = [(min(x), max(y)), (max(x), max(y)), (max(x), min(y))]
    return room_vectors


def min_max_mean(vector):  # [(x1, y1), (x2, y2)] -> x = [mix(x), max(x)], y = [mix(y), max(y)]
    x = [_[0] for _ in vector]
    y = [_[1] for _ in vector]
    return [min(x), max(x)], [min(y), max(y)]


def find_centers_points(min_max_x, min_max_y, step=1):
    centroid = step / 2
    return [[x + centroid - 1, y + centroid - 1]
            for x in np.arange(min_max_x[0] + 1, min_max_x[1], step)
            for y in np.arange(min_max_y[0] + 1, min_max_y[1], step)]


def draw_map(x: list, y: list, object_position=[0, 0], min_max_x=[-2, 2], min_max_y=[-2, 2], robot=[], glob_p = global_path,
             points_x=[0.5], points_y=[0.5], step=1,
             grid=True, points=True, object_positon_show=True, robor_position=True,
             draw_path_show = True, get_path = True):
    """
    x, y - координаты кубико расположенных по контуру карты для получения информации о ней
    object_position -  положение объекта на карте который необходимо найти
    min_max_x, min_max_y - краевые точки карты
    robot - координаты робота
    glob_p - построенный путь
    points_x, points_y - расстояние на которое происходит отступ точки от ячейки
    step - шаг дискретизации карты
    *args - отрисока элементов карты по отдельности
    """

    fig, axes = plt.subplots()

    def draw_vectors_poligon(min_max_x, min_max_y, step, color='gray'):  # отрисовка ячеек
        for i in np.arange(min_max_x[0], min_max_x[1], step):
            axes.plot([i, i], min_max_y, color=color, linewidth=1)
        for i in np.arange(min_max_y[0], min_max_y[1], step):
            axes.plot(min_max_x, [i, i], color=color, linewidth=1)

    def draw_robot(robot):
        robot.append(robot[0])
        rob_x = [i[0] for i in robot]
        rob_y = [i[1] for i in robot]
        axes.plot(rob_x, rob_y)

    def onMouseClick(event: matplotlib.backend_bases.MouseEvent) -> None: # получение пути с matplotlib
        global global_path
        x = event.xdata
        y = event.ydata
        global_path.append([x, y])

    def draw_path(glob_p): # Отрисовка полученного пути
        gl_x = [i[0] for i in glob_p]
        gl_y = [i[1] for i in glob_p]
        axes.plot(gl_x, gl_y)

    if grid:
        draw_vectors_poligon(min_max_x, min_max_y, step)
    if points:
        axes.scatter(points_x, points_y, s=3, color='green')
    if object_positon_show:
        axes.scatter(object_position[0], object_position[1], s=40, color='red')
    if robor_position:
        draw_robot(robot)
    if draw_path_show:
        draw_path(glob_p)
    axes.plot(x, y, linewidth=4, color='black')

    if get_path:
        fig.canvas.mpl_connect('button_press_event', onMouseClick)

x, y = cuboids_parser(20)
edges = edge_room_descritesation(x, y)
min_max_x, min_max_y = min_max_mean(edges)
points_x, points_y = prepare_vector_massiv_to_x_y_vector(find_centers_points(min_max_x, min_max_y, step=1))

draw_map(x, y, object_position=[f_x, f_y], min_max_x=min_max_x, min_max_y=min_max_y, robot=wheelJoints_coords,
         points_x=points_x, points_y=points_y, glob_p=global_path, step=1, points=True, grid=True,
         object_positon_show=False, robor_position=False)
plt.show()

draw_map(x, y, object_position=[f_x, f_y], min_max_x=min_max_x, min_max_y=min_max_y, robot=wheelJoints_coords,
         points_x=points_x, points_y=points_y, glob_p=global_path, step=1, points=True, grid=True,
         get_path=False)
plt.show()




