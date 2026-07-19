from sqlalchemy import text


def is_file_processed(engine, file_name):
    query = text("""
        SELECT COUNT(*)
        FROM audit.processed_files
        WHERE file_name = :file_name
          AND status = 'processed'
    """)
    with engine.connect() as conn:
        return conn.execute(query, {'file_name': file_name}).scalar() > 0


def register_file(engine, file_name, source_block, status='processed'):
    query = text('''
        INSERT INTO audit.processed_files(file_name, source_block, status)
        VALUES (:file_name, :source_block, :status)
    ''')
    with engine.begin() as conn:
        conn.execute(query, {
            'file_name': file_name,
            'source_block': source_block,
            'status': status
        })
