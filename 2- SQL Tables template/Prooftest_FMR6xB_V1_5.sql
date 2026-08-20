USE [ProofTest]
GO
/****** Object:  Table [dbo].[FMR6xB_V1_5]    Script Date: auto-generated ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FMR6xB_V1_5](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Actual_Value_1] [decimal](10, 3) NULL,
	[Actual_Value_2] [decimal](10, 3) NULL,
	[Actual_Value_3] [decimal](10, 3) NULL,
	[Actual_Value_4] [decimal](10, 3) NULL,
	[Actual_Value_5] [decimal](10, 3) NULL,
	[Alarm_Selection] [int] NULL,
	[Block_Error] [int] NULL,
	[Block_Running] [int] NULL,
	[Builtup_Detection] [decimal](10, 3) NULL,
	[Builtup_Detection_Activated] [int] NULL,
	[CRC_After_Test] [int] NULL,
	[CRC_Before_Test] [int] NULL,
	[Current_Step] [int] NULL,
	[Damping_Value] [decimal](10, 3) NULL,
	[Device_ID] [bigint] NULL,
	[Device_Revision] [int] NULL,
	[Device_Status] [int] NULL,
	[Device_Type] [int] NULL,
	[Enabled] [bit] NULL,
	[End_Timestamp] [bigint] NULL,
	[Error] [bit] NULL,
	[Error_code] [bigint] NULL,
	[Hardware_Revision] [int] NULL,
	[Heartbeat_Verification_Result] [int] NULL,
	[Heartbeat_Verification_Timestamp] [bigint] NULL,
	[High_Error_Current] [decimal](10, 3) NULL,
	[Locking_Status] [int] NULL,
	[Long_Tag] [nvarchar](50) NULL,
	[Low_Error_Current] [decimal](10, 3) NULL,
	[Lower_Range_Value] [decimal](10, 3) NULL,
	[Max_Temperature] [decimal](10, 3) NULL,
	[Min_Temperature] [decimal](10, 3) NULL,
	[Parameters_After_Test] [nvarchar](50) NULL,
	[Parameters_Before_Test] [nvarchar](50) NULL,
	[Precision] [decimal](10, 3) NULL,
	[RAW_Value] [bigint] NULL,
	[Response_Code] [int] NULL,
	[Running] [bit] NULL,
	[Serial_Number] [nvarchar](50) NULL,
	[Software_Revision] [int] NULL,
	[Start_Timestamp] [bigint] NULL,
	[Tag] [nvarchar](50) NULL,
	[Temperature_Unit] [int] NULL,
	[Test_Point_1] [decimal](10, 3) NULL,
	[Test_Point_2] [decimal](10, 3) NULL,
	[Test_Point_3] [decimal](10, 3) NULL,
	[Test_Point_4] [decimal](10, 3) NULL,
	[Test_Point_5] [decimal](10, 3) NULL,
	[Transfer_Function] [int] NULL,
	[Transmitter_Units_Code] [int] NULL,
	[Upper_Range_Value] [decimal](10, 3) NULL,
	[User_Level] [int] NULL,

	[Error_code_Byte4]  AS (CONVERT([int],[Error_code]/power((2),(24))&0xFF)) PERSISTED,
	[Error_code_Byte3]  AS (CONVERT([int],[Error_code]/power((2),(16))&0xFF)) PERSISTED,
	[Error_code_Byte2]  AS (CONVERT([int],[Error_code]/power((2),(8))&0xFF)) PERSISTED,
	[Error_code_Byte1]  AS (CONVERT([int],[Error_code]&0xFF)) PERSISTED
 CONSTRAINT [PK_FMR6xB_V1_5] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
