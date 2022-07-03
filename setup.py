from setuptools import setup

setup(
	name='abletondrumrack',
	version='1.0.2',
	author='Daniel Kavoulakos',
	author_email='dan_kavoulakos@hotmail.com',
	description='Create Ableton Live 11 Drum Rack presets.',
	url='https://github.com/danikavu/Ableton-Drum-Rack',
	license='MIT',
	packages=['.abletondrumrack'],
	package_data={'.abletondrumrack': ['ableton_files/*']},
	install_requires=[
		'numpy',
		'pandas',
		'SoundFile',
		],
	python_requires='>=3.7',
)
