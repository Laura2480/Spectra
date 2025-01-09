import numpy as np
import imageio
import cv2
import io
import colorsys
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
from sklearn.linear_model import LinearRegression


#Utility
colors = []
for j in np.linspace(1, 0, 100):
    colors.append((30./255, 136./255, 229./255,j))
for j in np.linspace(0, 1, 100):
    colors.append((255./255, 13./255, 87./255,j))
red_transparent_blue = LinearSegmentedColormap.from_list("red_transparent_blue", colors)

joint_pairs = [
               [0, 1], #right hip
               [1, 2], [2, 3], #right leg
               [0, 4], #left hip
               [4, 5], [5, 6], #left leg
               [0, 7], [7, 8],#torso
               [8, 9], # lower head
               [8, 11], [8, 14], #shoulders
               [9, 10], #top head
               [11, 12], [12, 13], #left arm
               [14, 15], [15, 16] #right arm
               ]
joint_pairs_left = [[8, 11], [11, 12], [12, 13], [0, 4], [4, 5], [5, 6]]
joint_pairs_right = [[8, 14], [14, 15], [15, 16], [0, 1], [1, 2], [2, 3]]
joint_pairs_colors = [
               (255,156,127), #right hip -
               (255,127,77), (255,77,36), #right leg -
               (77,222,255), #left hip
               (0,127,255),  (0,77,255), #left leg -
               (0, 215, 255), (0, 255, 204), #torso
               (77,255,222), #lower head -
               (0, 134, 255), (0, 255, 50), #shoulders -
               (91,252,235), #top head
               (77,135,255),(77,196,255), #left arm
               (77,255,77),(191,255,77) #right arm
               ]

p_colors=[
        (255,156,127),
        (255,127,77),
        (255,77,36),
        (255,77,36),
        (0,127,255),
        (0,77,255),
        (0,77,255),
        (0, 255, 204),
        (0, 194, 152),
        (91,252,235),
        (77,255,222),
        (77,135,255),
        (77,196,255),
        (77,196,255),
        (191,255,77),
        (77,255,77),
        (77,255,77)
        ]

H36_map={
        0: 'root',
        1: 'right hip',
        2: 'right knee',
        3: 'right ankle',
        4: 'left hip',
        5: 'left knee',
        6: 'left ankle',
        7: 'belly',
        8: 'neck',
        9: 'nose',
        10: 'head',
        11: 'left shoulder',
        12: 'left elbow',
        13: 'left wrist',
        14: 'right shoulder',
        15: 'right elbow',
        16: 'right wrist'}

action_names=[
            "drink water",
            "eat meal",
            "brush teeth",
            "brush hair",
            "drop",
            "pick up",
            "throw",
            "sit down",
            "stand up",
            "clapping",
            "reading",
            "writing",
            "tear up paper",
            "put on jacket",
            "take off jacket",
            "put on a shoe",
            "take off a shoe",
            "put on glasses",
            "take off glasses",
            "put on a hat/cap",
            "take off a hat/cap",
            "cheer up",
            "hand waving",
            "kicking something",
            "reach into pocket",
            "hopping",
            "jump up",
            "phone call",
            "play with phone/tablet",
            "type on a keyboard",
            "point to something",
            "taking a selfie",
            "check time (from watch)",
            "rub two hands",
            "nod head/bow",
            "shake head",
            "wipe face",
            "salute",
            "put palms together",
            "cross hands in front",
            "sneeze/cough",
            "staggering",
            "falling down",
            "headache",
            "chest pain",
            "back pain",
            "neck pain",
            "nausea/vomiting",
            "fan self",
            "punch/slap",
            "kicking",
            "pushing",
            "pat on back",
            "point finger",
            "hugging",
            "giving object",
            "touch pocket",
            "shaking hands",
            "walking towards",
            "walking apart"
            ]
def get_action_names():
    return action_names

def sample_color(v_min,v_max,val):

    val_norm = (((val - v_min) / (v_max - v_min))*2)-1
    return red_transparent_blue(val_norm)
    #return  np.append(mixed_color, alpha_combinato)

def plot_gradient_segments(ax, points, colors, segments_per_line=10):
      start_color, end_color = colors[0], colors[1]
      for j in np.linspace(0, 1, segments_per_line,endpoint=False):
          start_point = points[0] + (points[1] - points[0]) * j
          end_point = points[0] + (points[1] - points[0]) * (j + 1.0 / segments_per_line)
          start_point=start_point[[0, 2, 1]]
          start_point=-start_point

          end_point=end_point[[0, 2, 1]]
          end_point=-end_point

          segment = [start_point, end_point]
          color = (np.array(start_color) * (1 - j)) + (np.array(end_color) * j)
          ax.plot(*zip(*segment),lw=3, color=color)

def get_img_from_fig(fig, dpi=120):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0)
    buf.seek(0)
    img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    buf.close()
    img = cv2.imdecode(img_arr, 1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    return img

def fix_leaning(motion):
  nf=motion.shape[0]
  yz_coordinates = motion[:, [0, 7, 8], 1:]
  yz_coordinates_reshaped = yz_coordinates.reshape(-1, 2)
  X = yz_coordinates_reshaped[:, 0].reshape(-1, 1)
  y = yz_coordinates_reshaped[:, 1]

  model = LinearRegression().fit(X, y)
  angle = -np.arctan(model.coef_[0])
  rotation_matrix = np.array([[1, 0, 0],
                              [0, np.cos(angle), -np.sin(angle)],
                              [0, np.sin(angle), np.cos(angle)]])
  return np.dot(motion.reshape(-1, 3), rotation_matrix.T).reshape(nf, 17, 3)

def top_n_indices(arr, n):
    u_val,u_idx = np.unique([arr[f,j] for f,j in enumerate(np.argmax(arr, axis=1))],return_index=True)
    return u_idx[-n:]

def apply_shap_on_3d(motion,shap_values,index,video_path,elev=12, azim=90,fig_size=10):

    reader = imageio.get_reader(video_path)
    image_list=[]
    for i in index:
      image_list.append(reader.get_data(i if i < 223 else 222))
    reader.close()


    motion=fix_leaning(motion)
    motion= motion[index]
    max_val = np.nanpercentile(np.abs(shap_values.sum(-1)).flatten(), 99.9)
    shap_values=shap_values[index]

    base_gray = np.array([0.5, 0.5, 0.5, 0.5])  # RGBA
    shap_grid=np.abs(shap_values.sum(-1)) # shap (N,17,3)- > (N,17)

    motion=np.moveaxis(motion, 0, -1) # motion: (N,17,3)- > (17,3,N)
    vlen = motion.shape[-1]

    img_arr=[]
    for f in range(vlen):
        j3d = motion[:,:,f]
        fig = plt.figure(0, figsize=(fig_size, fig_size))
        ax = plt.axes(projection="3d")
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_zlim(-1, 1)
        ax.view_init(elev, azim)
        plt.tick_params(left = False, right = False , labelleft = False ,
                        labelbottom = False, bottom = False)
        for i in range(len(joint_pairs)):
            limb = joint_pairs[i]
            colors=[sample_color(-max_val,max_val,shap_grid[f,limb[0]]),sample_color(-max_val,max_val,shap_grid[f,limb[1]])]
            xs, ys, zs = [np.array([j3d[limb[0], j], j3d[limb[1], j]]) for j in range(3)]
            ax.plot(-xs, -zs, -ys, color=base_gray, lw=3, marker='o', markerfacecolor='w', markersize=3, markeredgewidth=2) # axis transformation for visualization
            ax.plot(-xs[0], -zs[0], -ys[0], color=colors[0], marker='o', markerfacecolor='w', markersize=3, markeredgewidth=2) # axis transformation for visualization
            ax.plot(-xs[1], -zs[1], -ys[1], color=colors[0], marker='o', markerfacecolor='w', markersize=3, markeredgewidth=2) # axis transformation for visualization
            points=[j3d[limb[0]],j3d[limb[1]]]

            plot_gradient_segments(ax, points, colors,)

        img_arr.append(get_img_from_fig(fig))

        plt.close()
    abs_vals = np.stack(np.abs(shap_values.sum(-1)) , 0).flatten()
    max_val = np.nanpercentile(abs_vals, 99.9)
    num_figure = len(img_arr)
    num_righe_figure = np.ceil(num_figure / 4).astype(int)

    # Crea una figura
    fig = plt.figure(figsize=(fig_size*4, fig_size*(2*num_righe_figure)))

    # Crea una griglia di subplot per le immagini
    gs = gridspec.GridSpec(2*num_righe_figure, 4, figure=fig)

    # Genera gli subplot per le immagini
    for i in range(num_righe_figure):
        for j in range(4):
            idx = i * 4 + j
            if idx < num_figure:
                ax = fig.add_subplot(gs[i, j])
                ax.set_title(f'\nFrame {index[idx]}\n',fontsize=64)
                ax.imshow(img_arr[idx])
                ax.axis('off')

                ax_im = fig.add_subplot(gs[i+num_righe_figure, j])
                #ax_im.set_title(f'Frame N = {index[idx]}\n',fontsize=56)
                ax_im.imshow(image_list[idx])
                ax_im.axis('off')
            else:
                # Opzionale: Crea subplot vuoti se non ci sono abbastanza immagini
                ax = fig.add_subplot(gs[i, j])
                ax.axis('off')
                ax_im = fig.add_subplot(gs[i+num_righe_figure, j])
                ax_im.axis('off')

    red_transparent_blue
    plt.tight_layout()

    plt.show()

def extract_2d_frames(motion,shap_values,index,video_path,fig_size=10,delta=0,mono=False):

    reader = imageio.get_reader(video_path)
    shape=reader.get_data(0).shape
    ratio=shape[0]/shape[1]
    reader.close()

    motion=fix_leaning(motion)
    motion= motion[index]
    motion=np.moveaxis(motion, 0, -1) # motion: (N,17,3)- > (17,3,N)

    vlen = motion.shape[-1]
    img_arr=[]
    fig, ax = plt.subplots(figsize=(fig_size, fig_size))  # Crea una figura e un asse 2D
    #ax.spines[:].set_visible(False)
    plt.grid(True)
    plt.tick_params(left=False, right=False, labelleft=False, labelbottom=False, bottom=False)

    rgb = (47,112,175)
    alpha_values = [1.0 - 0.8 * i / (vlen - 1) for i in range(vlen)]



    for i,f in enumerate(range(vlen)):
        j2d = motion[:, :2, f]  # Estrai le coordinate delle giunture per il frame attuale
        for j,limb in enumerate(joint_pairs):
            # Considera solo x e y per il plotting
            x = -np.array([j2d[limb[0], 0], j2d[limb[1], 0]])
            y = -np.array([j2d[limb[0], 1], j2d[limb[1], 1]])
            x=x-i*delta

            if not mono:
              rgb=joint_pairs_colors[j]
              hsv = colorsys.rgb_to_hsv(*(x / 255.0 for x in rgb))
              rgb_scurito = colorsys.hsv_to_rgb(hsv[0], hsv[1], max(0, hsv[2] * 0.75))
              rgb= tuple(int(x * 255) for x in rgb_scurito)

            rgba=rgb+(int(round(alpha_values[i] * 255)),)
            color = '#{0:02x}{1:02x}{2:02x}{3:02x}'.format(*rgba)

            ax.scatter(x, y, color= color, s=250)  # s è la dimensione del marker
            ax.plot(x, y, color=color,lw=5)


            #img_arr.append(get_img_from_fig(fig))
    plt.axis('equal')
    plt.show()

def extract_3d_frames(motion,shap_values,index,video_path,elev=12, azim=90,fig_size=10,delta=0,mono=False):

    reader = imageio.get_reader(video_path)
    shape=reader.get_data(0).shape
    ratio=shape[0]/shape[1]
    reader.close()

    motion=fix_leaning(motion)
    motion= motion[index]
    motion=np.moveaxis(motion, 0, -1) # motion: (N,17,3)- > (17,3,N)

    vlen = motion.shape[-1]

    img_arr=[]

    fig = plt.figure(0, figsize=(fig_size, fig_size))
    ax = plt.axes(projection="3d")
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)
    ax.view_init(elev, azim)
    plt.tick_params(left = False, right = False , labelleft = False ,labelbottom = False, bottom = False)

    rgb = (47,112,175)

    alpha_values = [1.0 - 0.8 * i / (vlen - 1) for i in range(vlen)]

    for q,f in enumerate(range(vlen)):
        j3d = motion[:,:,f]

        for i in range(len(joint_pairs)):
            limb = joint_pairs[i]

            if not mono:
              rgb=joint_pairs_colors[i]
              hsv = colorsys.rgb_to_hsv(*(x / 255.0 for x in rgb))
              rgb_scurito = colorsys.hsv_to_rgb(hsv[0], hsv[1], max(0, hsv[2] * 0.75))
              rgb= tuple(int(x * 255) for x in rgb_scurito)

            rgba=rgb+(int(round(alpha_values[q] * 255)),)
            color = '#{0:02x}{1:02x}{2:02x}{3:02x}'.format(*rgba)

            xs, ys, zs = [np.array([j3d[limb[0], j], j3d[limb[1], j]]) for j in range(3)]
            zs=zs+q*delta
            ax.plot(-xs, -zs, -ys, color=color, lw=3, marker='o', markerfacecolor='w', markersize=3, markeredgewidth=2) # axis transformation for visualization

    plt.show()

