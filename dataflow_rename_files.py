import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

class RenameFilesOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_argument('--source_bucket', required=True, help='Source GCS bucket')
        parser.add_argument('--destination_bucket', required=True, help='Destination GCS bucket')

def rename_file(file):
    new_name = 'new_prefix/' + file.metadata.resource_id.filename.replace(':', '_').replace('-', '_')
    return beam.io.WriteToText(f'{options.destination_bucket}/{new_name}')

options = RenameFilesOptions()

with beam.Pipeline(options=options) as p:
    files = p | 'Read files' >> beam.io.ReadFromText(options.source_bucket)
    renamed_files = files | 'Rename files' >> beam.Map(rename_file)
