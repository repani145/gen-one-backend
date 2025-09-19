import pandas as pd
import sqlalchemy

# ----------------------------
# STEP 1: Load Excel
# ----------------------------
excel_file = "migration_data.xlsx"
xls = pd.ExcelFile(excel_file)

# Read mapping (skip row 1 if headers start from row 2)
mapping_df = pd.read_excel(xls, sheet_name="mapping", skiprows=1)

# Build tab -> table -> field mapping
tab_table_map = {}
for _, row in mapping_df.iterrows():
    tab = row["tab"]
    src_field = row["field_id"]
    target_table = row["sap_table"]
    target_field = row["sap_field_id"]

    if pd.notna(target_table) and pd.notna(target_field):
        continue

    if tab not in tab_table_map:
        tab_table_map[tab] = {}

    if target_table not in tab_table_map[tab]:
        tab_table_map[tab][target_table] = {}

    if pd.notna(target_table) and pd.notna(target_field):
        tab_table_map[tab][target_table][src_field] = target_field

	# if !target_table && !target_field :
	# 	tab_table_map[tab][target_table][src_field] = target_field

# ----------------------------
# STEP 2: Process Each Tab
# ----------------------------
staging_data = {}

for tab_name in xls.sheet_names:
    if tab_name == "mapping":
        continue

    df = pd.read_excel(xls, sheet_name=tab_name)

    if tab_name not in tab_table_map:
        continue  # no mapping defined for this tab

    for target_table, field_map in tab_table_map[tab_name].items():
        mapped_df = pd.DataFrame()

        for src_field, target_field in field_map.items():
            if src_field in df.columns:
                mapped_df[target_field] = df[src_field]

        if target_table not in staging_data:
            staging_data[target_table] = mapped_df
        else:
            staging_data[target_table] = pd.concat([staging_data[target_table], mapped_df], ignore_index=True)

# ----------------------------
# STEP 3: Insert Into Database
# ----------------------------
# Example for SAP HANA connection

engine = sqlalchemy.create_engine("hana+pyhdb://user:pass@hostname:30015")

for table, df in staging_data.items():
    print(f"Inserting {len(df)} rows into {table}...")
    df.to_sql(table, con=engine, if_exists="append", index=False)

# NEW
# def get(self, request, *args, **kwargs):
#         # print("➡️ Entered DataLoad GET method")

#         object_name_id = request.GET.get("objectName")
#         if not object_name_id:
#             return Response(
#                 {"success": 0, "message": "❌ objectName is required.", "data": {}},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             # ----------------------------
#             # STEP 0: Get Object Name
#             # ----------------------------
#             object_name_qry = models.DataObject.objects.filter(id=object_name_id).first()
#             object_name = object_name_qry.objectName if object_name_qry else None
#             # print(f"🔍 Object Name Resolved: {object_name}")

#             working_info = create_and_get_working_file_path(object_name_id)
#             if not working_info or not os.path.exists(working_info["working_file_path"]):
#                 # print(f"❌ Working file not found for object: {object_name}")
#                 return Response(
#                     {"success": 0, "message": f"❌ Working file not found for {object_name}", "data": {}},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             file_path = working_info["working_file_path"]
#             # print(f"📂 Using working file: {file_path}")

#             # ----------------------------
#             # STEP 1: Load Excel + Build Mapping
#             # ----------------------------
#             # print("📑 Reading Excel...")
#             with pd.ExcelFile(file_path) as xls:
#                 mapping_df = pd.read_excel(xls, sheet_name="mapping")
#                 # print("✅ Mapping sheet loaded")
#                 # print(mapping_df.head())

#                 tab_table_map = {}
#                 # print("🔄 Building mapping dictionary...")
#                 for _, row in mapping_df.iterrows():
#                     tab = row["tab"]
#                     src_field = row["field_id"]
#                     target_table = row["sap_table"]
#                     target_field = row["sap_field_id"]

#                     if pd.isna(target_table) or pd.isna(target_field):
#                         # print(f"⚠️ Skipping unmapped row: {row.to_dict()}")
#                         continue

#                     if tab not in tab_table_map:
#                         tab_table_map[tab] = {}

#                     if target_table not in tab_table_map[tab]:
#                         tab_table_map[tab][target_table] = {}

#                     tab_table_map[tab][target_table][src_field] = target_field

#                 # print("✅ Mapping dictionary created")
#                 # print(tab_table_map)

#                 # ----------------------------
#                 # STEP 2: Process Tabs
#                 # ----------------------------
#                 staging_data = {}
#                 # print("🔄 Processing sheet tabs...")
#                 for tab_name in xls.sheet_names:
#                     if tab_name == "mapping":
#                         continue

#                     # print(f"📑 Processing Tab: {tab_name}")
#                     df = pd.read_excel(xls, sheet_name=tab_name)
#                     # print(f"   ➡️ Loaded {len(df)} rows from {tab_name}")

#                     if tab_name not in tab_table_map:
#                         # print(f"⚠️ No mapping found for tab {tab_name}, skipping...")
#                         continue

#                     for target_table, field_map in tab_table_map[tab_name].items():
#                         mapped_df = pd.DataFrame()
#                         # print(f"   🔄 Mapping for Target Table: {target_table}")

#                         for src_field, target_field in field_map.items():
#                             if src_field in df.columns:
#                                 mapped_df[target_field] = df[src_field]
#                                 # print(f"      ✅ Mapped {src_field} → {target_field}")
#                             else:
#                                 # print(f"      ⚠️ Source field {src_field} not found in tab {tab_name}")

#                         if target_table not in staging_data:
#                             staging_data[target_table] = mapped_df
#                         else:
#                             staging_data[target_table] = pd.concat(
#                                 [staging_data[target_table], mapped_df],
#                                 ignore_index=True,
#                             )

#                 # print("✅ All tabs processed")
#                 # print("📊 Staging Data Summary:")
#                 for k, v in staging_data.items():
#                     # print(f"   - {k}: {len(v)} rows")

#             # ----------------------------
#             # STEP 3: Insert Into Database
#             # ----------------------------
#             # print("🔌 Connecting to SAP HANA...")
#             # engine = sqlalchemy.create_engine("hana+pyhdb://user:pass@hostname:30015")
#             engine = sqlalchemy.create_engine("mysql+pymysql://root:Siva@localhost:3308/sap_db1")
#             # print("✅ DB Connection established")

#             result_summary = {}
#             for table, df in staging_data.items():
#                 try:
#                     if df.empty:
#                         # print(f"⚠️ Skipping {table} (0 rows)")
#                         continue

#                     # print(f"📥 Inserting {len(df)} rows into {table}...")
#                     df.to_sql(table, con=engine, if_exists="append", index=False)
#                     # print(f"✅ Inserted {len(df)} rows into {table}")
#                     result_summary[table] = len(df)

#                 except Exception as e:
#                     err_str = str(e)
#                     # print(f"❌ Error while inserting into {table}: {err_str}")

#                     if "Duplicate entry" in err_str:
#                         msg = f"❌ Duplicate entry error while inserting into {table} (Primary Key violation)"
#                     elif "Unknown column" in err_str:
#                         msg = f"❌ Column mismatch while inserting into {table} (check mapping vs DB schema)"
#                     elif "doesn't exist" in err_str or "not found" in err_str.lower():
#                         msg = f"❌ Target table {table} does not exist in database"
#                     else:
#                         msg = f"❌ Unexpected error while inserting into {table}: {err_str}"

#                     return Response({"success": 0, "message": msg, "data": {}}, status=500)

#             # print("✅ Data Load Completed Successfully")
#             # print("📊 Final Insert Summary:", result_summary)

#             return Response(
#                 {
#                     "success": 1,
#                     "message": f"✅ Data load completed for {object_name}",
#                     "data": {"staging_summary": result_summary},
#                 },
#                 status=200,
#             )

#         except Exception as e:
#             # print(f"💥 Critical Error: {str(e)}")
#             return Response(
#                 {"success": 0, "message": f"❌ Error: {str(e)}", "data": {}},
#                 status=500,
#             )


# old

# def get(self, request, *args, **kwargs):
#         print("➡️ Entered DataLoad GET method")

#         object_name_id = request.GET.get("objectName")
#         if not object_name_id:
#             print("❌ objectName not provided")
#             return Response(
#                 {"success": 0, "message": "❌ objectName is required.", "data": {}},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             object_name_qry = models.DataObject.objects.filter(id=object_name_id).first()
#             if object_name_qry:
#                 object_name = object_name_qry.objectName   # access model field directly
#             else:
#                 object_name = None
#             print(f"🔍 Creating/Fetching working file for object: {object_name}")
#             working_info = create_and_get_working_file_path(object_name_id)

#             if not working_info or not os.path.exists(working_info["working_file_path"]):
#                 print("❌ Working file not found")
#                 return Response(
#                     {"success": 0, "message": f"❌ Working file not found for {object_name}", "data": {}},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             file_path = working_info["working_file_path"]
#             print(f"📂 Working file located: {file_path}")

#             # ----------------------------
#             # STEP 1: Load Excel
#             # ----------------------------
#             print("📥 Loading Excel file...")
#             with pd.ExcelFile(file_path) as xls:
#                 print("📑 Reading mapping sheet...")
#                 mapping_df = pd.read_excel(xls, sheet_name="mapping")
#                 print("Columns in mapping_df:", mapping_df.columns.tolist())

#                 # ----------------------------
#                 # Build tab -> table -> field mapping
#                 # ----------------------------
#                 tab_table_map = {}
#                 print(mapping_df.iterrows())
#                 for _, row in mapping_df.iterrows():
#                     print('-------------------------------------------------------------------------->>>>ROW')
#                     print(row)
#                     # break
#                     tab = row["tab"]
#                     src_field = row["field_id"]
#                     target_table = row["sap_table"]     
#                     target_field = row["sap_field_id"]

#                     if pd.isna(target_table) or pd.isna(target_field):
#                         continue
#                         # tab_table_map[tab][target_table][src_field] = target_field

#                     if tab not in tab_table_map:
#                         tab_table_map[tab] = {}

#                     if target_table not in tab_table_map[tab]:
#                         tab_table_map[tab][target_table] = {}

#                     # if target_table and target_field:
#                     #     tab_table_map[tab][target_table][src_field] = target_field
                    
#                     if  target_table and target_field:
#                         tab_table_map[tab][target_table][src_field] = target_field

#                 print("✅ Mapping built successfully")

#                 # ----------------------------
#                 # STEP 2: Process Each Tab
#                 # ----------------------------
#                 staging_data = {}
#                 print("🔄 Processing each tab in Excel...")

#                 for tab_name in xls.sheet_names:
#                     print(f"➡️ Processing tab: {tab_name}")
#                     if tab_name == "mapping":
#                         print("⏩ Skipping mapping tab")
#                         continue

#                     df = pd.read_excel(xls, sheet_name=tab_name)

#                     # if tab_name not in tab_table_map:
#                     #     print(f"⚠️ No mapping defined for tab: {tab_name}, skipping...")
#                     #     continue

#                     for target_table, field_map in tab_table_map[tab_name].items():
#                         print(f"📊 Mapping data to target table: {target_table}")
#                         mapped_df = pd.DataFrame()

#                         for src_field, target_field in field_map.items():
#                             if src_field in df.columns:
#                                 mapped_df[target_field] = df[src_field]
#                                 print(f"   🔗 Mapped {src_field} ➝ {target_field}")
#                             else:
#                                 print(f"   ⚠️ Source field {src_field} not in {tab_name}, skipping...")

#                         if target_table not in staging_data:
#                             staging_data[target_table] = mapped_df
#                         else:
#                             staging_data[target_table] = pd.concat(
#                                 [staging_data[target_table], mapped_df],
#                                 ignore_index=True,
#                             )

#             print("✅ All tabs processed successfully")


#             # Remove invalid / NaN table keys
#             staging_data = {
#                 str(table): df 
#                 for table, df in staging_data.items() 
#                 if pd.notna(table) and str(table).lower() != "nan"
#             }
#             # For now: return counts per staging table
#             result_summary = {table: len(df) for table, df in staging_data.items()}
#             print(f"📊 Staging summary (before DB insert): {result_summary}")

#             # ----------------------------
#             # STEP 3: Insert into MySQL (with validation)
#             # ----------------------------
#             print("🗄️ Connecting to MySQL database...")
#             engine = sqlalchemy.create_engine("mysql+pymysql://root:Siva@localhost:3308/sap_db1")

#             inspector = inspect(engine)

#             for table, df in staging_data.items():
#                 if df.empty:
#                     print(f"⚠️ Skipping {table} (0 rows)")
#                     continue

#                 df.columns = [
#                     str(c).strip() if pd.notna(c) else f"col_{i}"
#                     for i, c in enumerate(df.columns)
#                 ]

#                 print(f"📥 Inserting {len(df)} rows into table {table}...")

#                 try:
#                     df.to_sql(table, con=engine, if_exists="append", index=False)
#                     print(f"✅ Inserted {len(df)} rows into {table}")
                
#                 except Exception as e:
#                     err_str = str(e)

#                     if "Duplicate entry" in err_str:
#                         msg = f"❌ Duplicate entry error while inserting into {table} (Primary Key violation)"
#                     elif "Unknown column" in err_str:
#                         msg = f"❌ Column mismatch while inserting into {table} (check mapping vs DB schema)"
#                     elif "doesn't exist" in err_str:
#                         msg = f"❌ Target table {table} does not exist in database"
#                     else:
#                         msg = f"❌ Unexpected error while inserting into {table}: {err_str.split(':')[0]}"

#                     print(msg)
#                     return Response(
#                         {"success": 0, "message": msg, "data": {}},
#                         status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     )

#                 except pymysql.err.IntegrityError as e:
#                     if e.args[0] == 1062:  # Duplicate entry
#                         msg = f"❌ Duplicate entry found while inserting into {table} (Primary Key violation)"
#                     else:
#                         msg = f"❌ Integrity error while inserting into {table}"
#                     print(msg)
#                     return Response(
#                         {"success": 0, "message": msg, "data": {}},
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#                 except pymysql.err.OperationalError as e:
#                     msg = f"❌ Database operational error while inserting into {table}: {e.args[1]}"
#                     print(msg)
#                     return Response(
#                         {"success": 0, "message": msg, "data": {}},
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#                 except Exception as e:
#                     msg = f"❌ Unexpected error while inserting into {table}: {str(e).split(':')[0]}"
#                     print(msg)
#                     return Response(
#                         {"success": 0, "message": msg, "data": {}},
#                         status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     )

#                 print("🎉 All data successfully validated and inserted into MySQL")

#             return Response(
#                 {
#                     "success": 1,
#                     "message": f"✅ Data load completed and inserted into MySQL for {object_name}.",
#                     "data": {
#                         "staging_summary": result_summary,
#                     },
#                 },
#                 status=status.HTTP_200_OK,
#             )

#         except Exception as e:
#             print(f"❌ Exception occurred: {str(e)}")
#             return Response(
#                 {"success": 0, "message": f"❌ Error: {str(e)}", "data": {}},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )
