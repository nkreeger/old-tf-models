import tensorflow as tf

# Pitch CSV column definitions
csv_column_types = [
  [''], # des (0)
  [],   # id (1)
  [''], # type (2)
  [''], # tfs_zulu (3)
  [],   # x (4)
  [],   # y (5)
  [],   # start_speed (6)
  [],   # end_speed (7)
  [],   # sz_top (8)
  [],   # sz_bot (9)
  [],   # pfx_x (10)
  [],   # pfx_z (11)
  [],   # px (12)
  [],   # pz (13)
  [],   # x0 (14)
  [],   # y0 (15)
  [],   # z0 (16)
  [],   # vx0 (17)
  [],   # vy0 (18)
  [],   # vz0 (19)
  [],   # ax (20)
  [],   # ay (21)
  [],   # az (22)
  [],   # break_y (23)
  [],   # break_angle (24)
  [],   # break_length (25)
  [''], # pitch_type (26)
  [0],  # pitch_code (27)
  [],   # type_confidence (28)
  [],   # zone (29)
  [],   # nasty (30)
  [],   # spin_dir (31)
  [],   # spin_rate (32)
]

NUM_PITCH_CLASSES = 11
PITCH_CLASSES = ['FF', 'SL', 'FT', 'CH', 'KN', 'CU', 'EP', 'FS', 'KC', 'SI', 'FC']

def decode_csv(line):
  parsed_line = tf.decode_csv(line, record_defaults=csv_column_types)

  pitch_code = parsed_line[27]
  label = tf.one_hot(pitch_code, NUM_PITCH_CLASSES)

  ax = parsed_line[20]
  ay = parsed_line[21]
  az = parsed_line[22]

  vx0 = parsed_line[17]
  vy0 = parsed_line[18]
  vz0 = parsed_line[19]

  px = parsed_line[12]
  pz = parsed_line[13]

  data = tf.stack([ax, ay, az, vx0, vy0, vz0, px, pz])
  return label, data


def load_data(filename, batchsize=100):
  dataset = tf.data.TextLineDataset([filename])
  dataset = dataset.skip(1)
  dataset = dataset.map(decode_csv)
  dataset = dataset.batch(batchsize)
  return dataset


def estimator_cols():
  return [
      'vx0',
      'vy0',
      'vz0',
      'ax',
      'ay',
      'az',
  ]


def decode_csv_est(line):
  parsed_line = tf.decode_csv(line, record_defaults=csv_column_types)

  pitch_code = parsed_line[27]

  break_y = parsed_line[23]
  break_angle = parsed_line[24]
  break_length = parsed_line[25]

  ax = parsed_line[20]
  ay = parsed_line[21]
  az = parsed_line[22]

  vx0 = parsed_line[17]
  vy0 = parsed_line[18]
  vz0 = parsed_line[19]

  px = parsed_line[12]
  pz = parsed_line[13]

  start_speed = parsed_line[6]
  end_speed = parsed_line[7]

  conf = parsed_line[28]

  features = dict(zip(estimator_cols(), [
      vx0,
      vy0,
      vz0,
      ax,
      ay,
      az
      ]))

  return features, pitch_code


def csv_input_fn(filename, batchsize=100):
  dataset = tf.data.TextLineDataset([filename]).skip(1)
  dataset = dataset.map(decode_csv_est)
  dataset = dataset.shuffle(25000).repeat().batch(batchsize)
  return dataset


def csv_eval_fn(filename, batchsize=100):
  dataset = tf.data.TextLineDataset([filename]).skip(1)
  dataset = dataset.map(decode_csv_est)
  dataset = dataset.shuffle(1000).batch(batchsize)
  return dataset


def test_pitch():
  # FT / 0.943
  px = -1.496,
  pz = 2.793,
  vx0 = 3.183,
  vy0 = -135.149,
  vz0 = -2.005,
  ax = -16.296,
  ay = 29.576,
  az = -22.414,
  break_y = 23.8,
  break_angle = 34.4,
  break_length = 6.1,
  start_speed = 89.1 # hack
  end_speed = 87.3 # hack

  samples = [
    [-9.706,-135.569,-4.866,6.548,28.308,-14.883],
    [-9.375,-115.324,-2.395,-1.281,22.358,-39.066],
    [3.183,-135.149,-2.005,-16.296,29.576,-22.414],
    [5.09,-123.243,-6.224,-19.159,28.283,-25.269],
    [3.857,-116.851,-0.632,-1.749,22.639,-34.27],
    [0.664,-117.548,1.539,3.957,24.355,-40.877],
    [1.158,-91.701,1.385,-1.263,13.798,-30.613],
    [9.089,-120.985,-2.767,-11.007,23.257,-28.045],
    [3.902,-117.524,1.619,7.688,24.31,-40.42],
    [-3.94,-132.87,-1.45,18.93,30.41,-31.62],
    [7.254,-133.116,-6.822,2.01,30.686,-8.24],
    [5.94,6.75,-110.35,0.4,4.86,21.73]  
  ]

  features = dict(zip(estimator_cols(), samples))
  return tf.data.Dataset.from_tensors(features)
